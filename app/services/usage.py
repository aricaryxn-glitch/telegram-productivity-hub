from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True)
class UsageDecision:
    allowed: bool
    remaining: int
    reason: str


def is_premium(now: datetime, premium_until: datetime | None) -> bool:
    if premium_until is None:
        return False
    if premium_until.tzinfo is None:
        premium_until = premium_until.replace(tzinfo=timezone.utc)
    return premium_until > now


def decide_usage(
    *,
    daily_count: int,
    free_daily_limit: int,
    bonus_conversions: int,
    premium_until: datetime | None = None,
    now: datetime | None = None,
) -> UsageDecision:
    now = now or datetime.now(timezone.utc)
    if is_premium(now, premium_until):
        return UsageDecision(True, 999_999, "premium")

    remaining_free = max(free_daily_limit - daily_count, 0)
    remaining = remaining_free + max(bonus_conversions, 0)
    if remaining <= 0:
        return UsageDecision(False, 0, "daily_limit_reached")
    return UsageDecision(True, remaining - 1, "free_or_bonus")


def can_claim_daily(last_claim_at: datetime | None, today: date | None = None) -> bool:
    if last_claim_at is None:
        return True
    today = today or datetime.now(timezone.utc).date()
    return last_claim_at.date() < today
