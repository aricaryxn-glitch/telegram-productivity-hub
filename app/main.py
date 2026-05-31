import os
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.types import Update
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.api_tools import router as tools_router
from app.bot import configure_bot, create_dispatcher
from app.db import get_db, init_db
from app.models import ConversionJob, ReferralReward, UsageEvent, User
from app.repositories import add_premium_days, daily_usage_count, get_or_create_user, record_usage, remove_premium, set_banned
from app.services.usage import decide_usage


app = FastAPI(title=get_settings().app_name)
app.include_router(tools_router)


class UserIn(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    referral_code: str | None = None


class JobIn(BaseModel):
    telegram_id: int
    feature: str
    input_path: str | None = None


class PremiumIn(BaseModel):
    telegram_id: int
    days: int


class UserModerationIn(BaseModel):
    telegram_id: int


@app.on_event("startup")
async def startup() -> None:
    init_db()
    settings = get_settings()
    webhook_base_url = settings.webhook_base_url or os.getenv("RENDER_EXTERNAL_URL", "")
    if settings.bot_token and webhook_base_url:
        bot = Bot(settings.bot_token)
        dispatcher = create_dispatcher()
        webhook_url = f"{webhook_base_url.rstrip('/')}/telegram/webhook"
        webhook_secret = settings.telegram_safe_webhook_secret
        await configure_bot(bot)
        await bot.set_webhook(
            webhook_url,
            secret_token=webhook_secret or None,
            drop_pending_updates=False,
        )
        app.state.telegram_bot = bot
        app.state.telegram_dispatcher = dispatcher
        app.state.telegram_webhook_url = webhook_url


@app.on_event("shutdown")
async def shutdown() -> None:
    bot = getattr(app.state, "telegram_bot", None)
    if bot:
        await bot.session.close()


@app.get("/health")
def health() -> dict:
    return {"ok": True, "time": datetime.now(timezone.utc).isoformat()}


@app.head("/health")
def health_head() -> Response:
    return Response(status_code=200)


@app.get("/")
def root() -> dict:
    return {"ok": True, "service": get_settings().app_name}


@app.head("/")
def root_head() -> Response:
    return Response(status_code=200)


@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    settings = get_settings()
    webhook_secret = settings.telegram_safe_webhook_secret
    if webhook_secret and x_telegram_bot_api_secret_token != webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")
    bot = getattr(app.state, "telegram_bot", None)
    dispatcher = getattr(app.state, "telegram_dispatcher", None)
    if not bot or not dispatcher:
        raise HTTPException(status_code=503, detail="Telegram webhook is not configured")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dispatcher.feed_update(bot, update)
    return {"ok": True}


@app.post("/users")
def upsert_user(payload: UserIn, db: Session = Depends(get_db)) -> dict:
    user = get_or_create_user(
        db,
        telegram_id=payload.telegram_id,
        username=payload.username,
        first_name=payload.first_name,
        referral_code=payload.referral_code,
    )
    return {"id": user.id, "telegram_id": user.telegram_id, "referral_code": user.referral_code}


@app.post("/jobs")
def create_job(payload: JobIn, db: Session = Depends(get_db)) -> dict:
    settings = get_settings()
    user = get_or_create_user(db, telegram_id=payload.telegram_id)
    if user.is_banned:
        raise HTTPException(status_code=403, detail="User is banned")

    usage = daily_usage_count(db, user.id)
    decision = decide_usage(
        daily_count=usage,
        free_daily_limit=settings.free_daily_conversions,
        bonus_conversions=user.bonus_conversions,
        premium_until=user.premium_until,
    )
    if not decision.allowed:
        raise HTTPException(status_code=402, detail="Daily limit reached")

    if decision.reason == "free_or_bonus" and usage >= settings.free_daily_conversions and user.bonus_conversions > 0:
        user.bonus_conversions -= 1

    job = ConversionJob(user_id=user.id, feature=payload.feature, input_path=payload.input_path)
    db.add(job)
    db.commit()
    db.refresh(job)
    record_usage(db, user.id, payload.feature)
    return {"job_id": job.id, "status": job.status, "remaining": decision.remaining}


@app.post("/premium")
def grant_premium(payload: PremiumIn, db: Session = Depends(get_db)) -> dict:
    user = get_or_create_user(db, telegram_id=payload.telegram_id)
    add_premium_days(db, user, payload.days)
    return {"telegram_id": user.telegram_id, "premium_until": user.premium_until}


@app.delete("/premium/{telegram_id}")
def revoke_premium(telegram_id: int, db: Session = Depends(get_db)) -> dict:
    user = get_or_create_user(db, telegram_id=telegram_id)
    remove_premium(db, user)
    return {"telegram_id": user.telegram_id, "premium_until": user.premium_until}


@app.post("/ban")
def ban_user(payload: UserModerationIn, db: Session = Depends(get_db)) -> dict:
    user = get_or_create_user(db, telegram_id=payload.telegram_id)
    set_banned(db, user, True)
    return {"telegram_id": user.telegram_id, "is_banned": user.is_banned}


@app.post("/unban")
def unban_user(payload: UserModerationIn, db: Session = Depends(get_db)) -> dict:
    user = get_or_create_user(db, telegram_id=payload.telegram_id)
    set_banned(db, user, False)
    return {"telegram_id": user.telegram_id, "is_banned": user.is_banned}


@app.get("/stats")
def stats(db: Session = Depends(get_db)) -> dict:
    return {
        "users": db.scalar(select(func.count(User.id))) or 0,
        "usage_events": db.scalar(select(func.count(UsageEvent.id))) or 0,
        "jobs": db.scalar(select(func.count(ConversionJob.id))) or 0,
        "referrals": db.scalar(select(func.count(ReferralReward.id))) or 0,
    }
