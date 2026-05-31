from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="PDF Tools", callback_data="menu:pdf"),
            InlineKeyboardButton(text="Image Tools", callback_data="menu:image"),
        ],
        [
            InlineKeyboardButton(text="AI Tools", callback_data="menu:ai"),
            InlineKeyboardButton(text="Resume Center", callback_data="menu:resume"),
        ],
        [
            InlineKeyboardButton(text="Referral", callback_data="menu:referral"),
            InlineKeyboardButton(text="Credits", callback_data="menu:credits"),
        ],
        [InlineKeyboardButton(text="Daily Reward", callback_data="daily")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tool_menu(prefix: str, tools: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=label, callback_data=f"tool:{prefix}:{slug}")] for label, slug in tools]
    rows.append([InlineKeyboardButton(text="Back", callback_data="menu:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
