from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text="🎬 Kino qidirish")
    b.button(text="🔢 Kino kodi orqali")
    b.button(text="📂 Kategoriyalar")
    b.button(text="📺 Seriallar")
    b.button(text="💎 Premium")
    b.button(text="🎁 Promo kod")
    b.button(text="ℹ️ Yordam")
    if is_admin:
        b.button(text="⚙️ Admin panel")
        b.adjust(2, 2, 2, 1, 1, 1)
    else:
        b.adjust(2, 2, 2, 1, 1)
    return b.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text="❌ Bekor qilish")
    b.button(text="🏠 Asosiy menyu")
    b.adjust(2)
    return b.as_markup(resize_keyboard=True)


def categories_kb(categories) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for c in categories:
        b.button(text=c.name, callback_data=f"cat:{c.id}")
    b.adjust(2)
    return b.as_markup()


def movies_list_kb(movies) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for m in movies:
        badge = "💎 " if getattr(m, "is_premium", False) else ""
        b.button(text=f"{badge}{m.title} ({m.code})", callback_data=f"getmovie:{m.id}")
    b.adjust(1)
    return b.as_markup()


def series_list_kb(series_list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for s in series_list:
        badge = "💎 " if getattr(s, "is_premium", False) else ""
        b.button(text=f"{badge}{s.title} ({s.code})", callback_data=f"getseries:{s.id}")
    b.adjust(1)
    return b.as_markup()


def episodes_kb(episodes) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for e in episodes:
        b.button(text=f"{e.episode_number}-qism", callback_data=f"getepisode:{e.id}")
    b.adjust(4)
    return b.as_markup()


def premium_menu_kb(plans, is_premium: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in plans:
        price_val = getattr(p, "price", 0) or 0
        price_str = f"{price_val:,}".replace(",", " ")
        b.button(
            text=f"{plan_title(p.name)} ({p.duration_days} kun) — {price_str} so'm",
            callback_data=f"buypremium:{p.id}",
        )
    b.button(text="🎁 Promo kodni kiritish", callback_data="enter_promo")
    b.adjust(1)
    return b.as_markup()



def plan_title(name: str) -> str:
    return {
        "daily": "🗓 Kunlik",
        "weekly": "📆 Haftalik",
        "monthly": "📅 Oylik",
    }.get(name, name)


def subscribe_kb(channels, pending_type: str, pending_ref) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for ch in channels:
        raw = ch.username.strip()
        if raw.startswith("http"):
            link = raw
        else:
            link = f"https://t.me/{raw.lstrip('@')}"
        b.button(text=f"📢 {ch.title}", url=link)
    b.button(text="✅ Obunani tekshirish", callback_data=f"checksub:{pending_type}:{pending_ref}")
    b.adjust(1)
    return b.as_markup()
