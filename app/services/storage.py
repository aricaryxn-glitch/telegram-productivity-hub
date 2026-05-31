from pathlib import Path
from uuid import uuid4

from app.config import get_settings


def user_storage_dir(telegram_id: int) -> Path:
    root = get_settings().storage_dir / str(telegram_id)
    root.mkdir(parents=True, exist_ok=True)
    return root


def unique_path(telegram_id: int, suffix: str) -> Path:
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    return user_storage_dir(telegram_id) / f"{uuid4().hex}{suffix}"

