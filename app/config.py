from functools import lru_cache
import hashlib
from pathlib import Path
import re

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Telegram Productivity Hub"
    environment: str = "development"
    database_url: str = "sqlite:///./hub.db"
    redis_url: str = "redis://localhost:6379/0"
    bot_token: str = ""
    admin_ids: str = ""
    forced_channel: str = ""
    free_daily_conversions: int = 10
    referral_reward_conversions: int = 3
    referral_reward_premium_days: int = 0
    storage_dir: Path = Path("storage")
    ai_provider: str = "groq"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    ocr_languages: str = "eng+hin+rus+ara"
    remove_bg_api_key: str = ""
    webhook_base_url: str = ""
    telegram_webhook_secret: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def admin_id_set(self) -> set[int]:
        ids: set[int] = set()
        for value in self.admin_ids.split(","):
            value = value.strip()
            if value and value.lstrip("-").isdigit():
                ids.add(int(value))
        return ids

    @property
    def admin_username_set(self) -> set[str]:
        usernames: set[str] = set()
        for value in self.admin_ids.split(","):
            value = value.strip()
            if value and not value.lstrip("-").isdigit():
                usernames.add(value.removeprefix("@").lower())
        return usernames

    @property
    def forced_channel_chat(self) -> str:
        value = self.forced_channel.strip()
        if value.startswith("https://t.me/"):
            value = value.removeprefix("https://t.me/").split("/", maxsplit=1)[0]
        elif value.startswith("http://t.me/"):
            value = value.removeprefix("http://t.me/").split("/", maxsplit=1)[0]
        if value and not value.startswith("@") and not value.lstrip("-").isdigit():
            return f"@{value}"
        return value

    def is_admin(self, telegram_id: int, username: str | None = None) -> bool:
        if telegram_id in self.admin_id_set:
            return True
        if username and username.lower() in self.admin_username_set:
            return True
        return False

    @property
    def telegram_safe_webhook_secret(self) -> str:
        value = self.telegram_webhook_secret.strip()
        if not value:
            return ""
        if re.fullmatch(r"[A-Za-z0-9_-]{1,256}", value):
            return value
        return hashlib.sha256(value.encode("utf-8")).hexdigest()


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return settings
