from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ReferralReward, UsageEvent, User
from app.services.referrals import make_referral_code


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def get_or_create_user(
    db: Session,
    *,
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    referral_code: str | None = None,
) -> User:
    user = db.scalar(select(User).where(User.telegram_id == telegram_id))
    if user:
        user.username = username
        user.first_name = first_name
        db.commit()
        return user

    referred_by = None
    if referral_code:
        referred_by = db.scalar(select(User).where(User.referral_code == referral_code))

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        referral_code=make_referral_code(),
        referred_by_id=referred_by.id if referred_by else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if referred_by:
        settings = get_settings()
        referred_by.bonus_conversions += settings.referral_reward_conversions
        if settings.referral_reward_premium_days:
            now = datetime.now(timezone.utc)
            premium_until = _aware(referred_by.premium_until)
            base = premium_until if premium_until and premium_until > now else now
            referred_by.premium_until = base + timedelta(days=settings.referral_reward_premium_days)
        db.add(
            ReferralReward(
                referrer_id=referred_by.id,
                referred_user_id=user.id,
                conversions_awarded=settings.referral_reward_conversions,
                premium_days_awarded=settings.referral_reward_premium_days,
            )
        )
        db.commit()

    return user


def daily_usage_count(db: Session, user_id: int) -> int:
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return db.scalar(
        select(func.count(UsageEvent.id)).where(
            UsageEvent.user_id == user_id,
            UsageEvent.created_at >= start,
        )
    ) or 0


def record_usage(db: Session, user_id: int, feature: str) -> None:
    db.add(UsageEvent(user_id=user_id, feature=feature))
    db.commit()


def add_premium_days(db: Session, user: User, days: int) -> User:
    now = datetime.now(timezone.utc)
    premium_until = _aware(user.premium_until)
    base = premium_until if premium_until and premium_until > now else now
    user.premium_until = base + timedelta(days=days)
    db.commit()
    db.refresh(user)
    return user


def remove_premium(db: Session, user: User) -> User:
    user.premium_until = None
    db.commit()
    db.refresh(user)
    return user


def set_banned(db: Session, user: User, banned: bool) -> User:
    user.is_banned = banned
    db.commit()
    db.refresh(user)
    return user
