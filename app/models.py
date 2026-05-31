from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    referral_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    referred_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    coins: Mapped[int] = mapped_column(Integer, default=0)
    bonus_conversions: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_daily_claim_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    referred_by: Mapped["User | None"] = relationship(remote_side=[id])


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    feature: Mapped[str] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class ConversionJob(Base):
    __tablename__ = "conversion_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    feature: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(30), default=JobStatus.queued.value, index=True)
    input_path: Mapped[str | None] = mapped_column(Text)
    output_path: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReferralReward(Base):
    __tablename__ = "referral_rewards"

    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    referred_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    conversions_awarded: Mapped[int] = mapped_column(Integer, default=0)
    premium_days_awarded: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SponsoredButton(Base):
    __tablename__ = "sponsored_buttons"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(80))
    url: Mapped[str] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

