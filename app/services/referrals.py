import secrets
import string


ALPHABET = string.ascii_letters + string.digits


def make_referral_code(length: int = 10) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def make_referral_link(bot_username: str, code: str) -> str:
    return f"https://t.me/{bot_username}?start={code}"

