import asyncio
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.types import BotCommand, CallbackQuery, Message

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.keyboards import main_menu, tool_menu
from app.repositories import add_premium_days, daily_usage_count, get_or_create_user, remove_premium, set_banned
from app.services.referrals import make_referral_link
from app.services.usage import can_claim_daily


PDF_TOOLS = [
    ("Image to PDF", "image_to_pdf"),
    ("PDF to Images", "pdf_to_images"),
    ("Merge PDF", "merge_pdf"),
    ("Split PDF", "split_pdf"),
    ("Compress PDF", "compress_pdf"),
    ("Protect PDF", "protect_pdf"),
    ("Unlock PDF", "unlock_pdf"),
    ("Rotate PDF", "rotate_pdf"),
    ("Extract Pages", "extract_pages"),
]
IMAGE_TOOLS = [
    ("Convert Format", "convert_image"),
    ("Compress Image", "compress_image"),
    ("Resize Image", "resize_image"),
    ("Crop Image", "crop_image"),
    ("Watermark Image", "watermark_image"),
]
AI_TOOLS = [
    ("PDF Summarizer", "pdf_summary"),
    ("Notes Simplifier", "simplify_notes"),
    ("Quiz Generator", "quiz"),
    ("Flashcards", "flashcards"),
    ("Interview Prep", "interview"),
]
RESUME_TOOLS = [
    ("Resume Builder", "resume_builder"),
    ("ATS Scanner", "ats"),
    ("Resume Improver", "resume_improve"),
    ("Cover Letter", "cover_letter"),
    ("LinkedIn Profile", "linkedin"),
]


def _register_user(message: Message, referral_code: str | None = None):
    with SessionLocal() as db:
        return get_or_create_user(
            db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            referral_code=referral_code,
        )


async def start(message: Message, command: CommandObject) -> None:
    if not await _passes_channel_gate(message):
        return
    user = _register_user(message, command.args)
    await message.answer(
        f"Welcome, {user.first_name or 'friend'}.\n\nChoose a tool to begin.",
        reply_markup=main_menu(),
    )


async def daily(message: Message) -> None:
    if not await _passes_channel_gate(message):
        return
    settings = get_settings()
    with SessionLocal() as db:
        user = get_or_create_user(db, telegram_id=message.from_user.id)
        if not can_claim_daily(user.last_daily_claim_at):
            await message.answer("You already claimed today's reward. Come back tomorrow.")
            return
        user.last_daily_claim_at = datetime.now(timezone.utc)
        user.bonus_conversions += 3
        user.coins += 5
        user.streak_days += 1
        db.commit()
    await message.answer(f"Daily reward claimed: +3 conversions and +5 coins. Free daily limit: {settings.free_daily_conversions}.")


async def daily_callback(callback: CallbackQuery) -> None:
    settings = get_settings()
    with SessionLocal() as db:
        user = get_or_create_user(
            db,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
        )
        if not can_claim_daily(user.last_daily_claim_at):
            await callback.message.answer("You already claimed today's reward. Come back tomorrow.")
            await callback.answer()
            return
        user.last_daily_claim_at = datetime.now(timezone.utc)
        user.bonus_conversions += 3
        user.coins += 5
        user.streak_days += 1
        db.commit()
    await callback.message.answer(f"Daily reward claimed: +3 extra tokens and +5 coins. Free daily limit: {settings.free_daily_conversions}.")
    await callback.answer()


async def stats(message: Message) -> None:
    settings = get_settings()
    if not settings.is_admin(message.from_user.id, message.from_user.username):
        return
    with SessionLocal() as db:
        from sqlalchemy import func, select
        from app.models import ConversionJob, ReferralReward, UsageEvent, User

        users = db.scalar(select(func.count(User.id))) or 0
        usage = db.scalar(select(func.count(UsageEvent.id))) or 0
        jobs = db.scalar(select(func.count(ConversionJob.id))) or 0
        referrals = db.scalar(select(func.count(ReferralReward.id))) or 0
    await message.answer(f"Stats\nUsers: {users}\nUsage events: {usage}\nJobs: {jobs}\nReferrals: {referrals}")


async def addpremium(message: Message, command: CommandObject) -> None:
    settings = get_settings()
    if not settings.is_admin(message.from_user.id, message.from_user.username):
        return
    if not command.args:
        await message.answer("Usage: /addpremium <telegram_id> <days>")
        return
    telegram_id, days = command.args.split(maxsplit=1)
    with SessionLocal() as db:
        user = get_or_create_user(db, telegram_id=int(telegram_id))
        add_premium_days(db, user, int(days))
    await message.answer("Premium updated.")


async def removepremium(message: Message, command: CommandObject) -> None:
    settings = get_settings()
    if not settings.is_admin(message.from_user.id, message.from_user.username):
        return
    if not command.args:
        await message.answer("Usage: /removepremium <telegram_id>")
        return
    with SessionLocal() as db:
        user = get_or_create_user(db, telegram_id=int(command.args.strip()))
        remove_premium(db, user)
    await message.answer("Premium removed.")


async def ban(message: Message, command: CommandObject) -> None:
    settings = get_settings()
    if not settings.is_admin(message.from_user.id, message.from_user.username):
        return
    if not command.args:
        await message.answer("Usage: /ban <telegram_id>")
        return
    with SessionLocal() as db:
        user = get_or_create_user(db, telegram_id=int(command.args.strip()))
        set_banned(db, user, True)
    await message.answer("User banned.")


async def unban(message: Message, command: CommandObject) -> None:
    settings = get_settings()
    if not settings.is_admin(message.from_user.id, message.from_user.username):
        return
    if not command.args:
        await message.answer("Usage: /unban <telegram_id>")
        return
    with SessionLocal() as db:
        user = get_or_create_user(db, telegram_id=int(command.args.strip()))
        set_banned(db, user, False)
    await message.answer("User unbanned.")


async def broadcast(message: Message, command: CommandObject) -> None:
    settings = get_settings()
    if not settings.is_admin(message.from_user.id, message.from_user.username):
        return
    if not command.args:
        await message.answer("Usage: /broadcast <message>")
        return
    await message.answer("Broadcast command accepted. For production, dispatch this through a background worker to avoid Telegram rate limits.")


async def _passes_channel_gate(message: Message) -> bool:
    settings = get_settings()
    forced_channel = settings.forced_channel_chat
    if not forced_channel or settings.is_admin(message.from_user.id, message.from_user.username):
        return True
    try:
        member = await message.bot.get_chat_member(forced_channel, message.from_user.id)
    except Exception:
        await message.answer(f"Join {forced_channel} to use this bot, then send /start again.")
        return False
    if member.status in {"left", "kicked"}:
        await message.answer(f"Join {forced_channel} to use this bot, then send /start again.")
        return False
    return True


async def handle_menu(callback: CallbackQuery) -> None:
    section = callback.data.split(":")[1]
    if section == "home":
        await callback.message.edit_text("Choose a tool to begin.", reply_markup=main_menu())
    elif section == "pdf":
        await callback.message.edit_text("PDF tools", reply_markup=tool_menu("pdf", PDF_TOOLS))
    elif section == "image":
        await callback.message.edit_text("Image tools", reply_markup=tool_menu("image", IMAGE_TOOLS))
    elif section == "ai":
        await callback.message.edit_text("AI tools", reply_markup=tool_menu("ai", AI_TOOLS))
    elif section == "resume":
        await callback.message.edit_text("Resume Center", reply_markup=tool_menu("resume", RESUME_TOOLS))
    elif section in {"credits", "premium"}:
        settings = get_settings()
        with SessionLocal() as db:
            user = get_or_create_user(db, telegram_id=callback.from_user.id)
            count = daily_usage_count(db, user.id)
            remaining_free = max(settings.free_daily_conversions - count, 0)
        await callback.message.edit_text(
            "Credits\n\n"
            f"Free daily conversions: {settings.free_daily_conversions}\n"
            f"Used today: {count}\n"
            f"Free remaining today: {remaining_free}\n"
            f"Bonus tokens: {user.bonus_conversions}\n\n"
            f"Each successful referral gives +{settings.referral_reward_conversions} bonus tokens. "
            "Bonus tokens are used only after the free daily tier is finished.",
            reply_markup=main_menu(),
        )
    elif section == "referral":
        me = await callback.bot.get_me()
        with SessionLocal() as db:
            user = get_or_create_user(db, telegram_id=callback.from_user.id)
            count = daily_usage_count(db, user.id)
        await callback.message.edit_text(
            "Your referral link:\n"
            f"{make_referral_link(me.username, user.referral_code)}\n\n"
            f"Today usage: {count}\n"
            f"Each successful referral gives +{get_settings().referral_reward_conversions} bonus tokens after your free tier is used.",
            reply_markup=main_menu(),
        )
    await callback.answer()


async def handle_tool(callback: CallbackQuery) -> None:
    _, group, slug = callback.data.split(":")
    await callback.message.answer(
        f"Selected: {slug}\n\nUpload the required file(s). The worker queue hook is ready; connect this callback to app.services.{group}_tools for production processing."
    )
    await callback.answer()


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.register(start, Command("start"))
    dp.message.register(daily, Command("daily"))
    dp.message.register(stats, Command("stats"))
    dp.message.register(addpremium, Command("addpremium"))
    dp.message.register(removepremium, Command("removepremium"))
    dp.message.register(ban, Command("ban"))
    dp.message.register(unban, Command("unban"))
    dp.message.register(broadcast, Command("broadcast"))
    dp.callback_query.register(handle_menu, F.data.startswith("menu:"))
    dp.callback_query.register(daily_callback, F.data == "daily")
    dp.callback_query.register(handle_tool, F.data.startswith("tool:"))
    return dp


async def configure_bot(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Open main menu"),
            BotCommand(command="daily", description="Claim daily reward"),
            BotCommand(command="stats", description="Admin statistics"),
            BotCommand(command="broadcast", description="Admin broadcast"),
            BotCommand(command="ban", description="Admin ban user"),
            BotCommand(command="unban", description="Admin unban user"),
        ]
    )


async def main() -> None:
    settings = get_settings()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required")
    init_db()
    bot = Bot(settings.bot_token)
    await bot.delete_webhook(drop_pending_updates=False)
    await configure_bot(bot)
    dp = create_dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
