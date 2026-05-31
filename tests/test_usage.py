from datetime import date, datetime, timedelta, timezone

from app.services.referrals import make_referral_code, make_referral_link
from app.services.usage import can_claim_daily, decide_usage
from app.config import Settings


def test_free_usage_allows_until_limit():
    decision = decide_usage(daily_count=3, free_daily_limit=10, bonus_conversions=0)
    assert decision.allowed is True
    assert decision.remaining == 6


def test_usage_blocks_after_limit():
    decision = decide_usage(daily_count=10, free_daily_limit=10, bonus_conversions=0)
    assert decision.allowed is False
    assert decision.reason == "daily_limit_reached"


def test_bonus_tokens_allow_usage_after_free_limit():
    decision = decide_usage(daily_count=10, free_daily_limit=10, bonus_conversions=3)
    assert decision.allowed is True
    assert decision.remaining == 2


def test_premium_bypasses_limit():
    decision = decide_usage(
        daily_count=100,
        free_daily_limit=10,
        bonus_conversions=0,
        premium_until=datetime.now(timezone.utc) + timedelta(days=1),
    )
    assert decision.allowed is True
    assert decision.reason == "premium"


def test_daily_claim_once_per_day():
    today = date(2026, 5, 31)
    assert can_claim_daily(None, today=today) is True
    assert can_claim_daily(datetime(2026, 5, 31, tzinfo=timezone.utc), today=today) is False
    assert can_claim_daily(datetime(2026, 5, 30, tzinfo=timezone.utc), today=today) is True


def test_referral_link_shape():
    code = make_referral_code()
    assert len(code) == 10
    assert make_referral_link("YourBot", code) == f"https://t.me/YourBot?start={code}"


def test_webhook_secret_is_telegram_safe():
    settings = Settings(telegram_webhook_secret="abc+/=bad")
    assert settings.telegram_safe_webhook_secret.isalnum()
    assert len(settings.telegram_safe_webhook_secret) == 64

    safe = Settings(telegram_webhook_secret="abc_DEF-123")
    assert safe.telegram_safe_webhook_secret == "abc_DEF-123"
