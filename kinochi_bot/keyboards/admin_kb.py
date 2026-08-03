from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_main_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🎬 Kinolar", callback_data="adm:movies")
    b.button(text="📺 Seriallar", callback_data="adm:series")
    b.button(text="📂 Kategoriyalar", callback_data="adm:categories")
    b.button(text="📢 Majburiy obuna", callback_data="adm:channels")
    b.button(text="💎 Premium", callback_data="adm:premium")
    b.button(text="🎁 Promo kodlar", callback_data="adm:promo")
    b.button(text="📣 Ommaviy xabar", callback_data="adm:broadcast")
    b.button(text="📊 Statistika", callback_data="adm:stats")
    b.button(text="⚙️ Sozlamalar", callback_data="adm:settings")
    b.adjust(2)
    return b.as_markup()


def back_to_admin_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    return b.as_markup()


def admin_movies_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Kino qo'shish", callback_data="adm_movie:add")
    b.button(text="✏️ Kino tahrirlash", callback_data="adm_movie:edit")
    b.button(text="🗑 Kino o'chirish", callback_data="adm_movie:delete")
    b.button(text="🔍 Kino qidirish", callback_data="adm_movie:search")
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    b.adjust(2, 2, 1)
    return b.as_markup()


def admin_series_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Serial qo'shish", callback_data="adm_series:add")
    b.button(text="✏️ Serial tahrirlash", callback_data="adm_series:edit")
    b.button(text="➕ Qism qo'shish", callback_data="adm_series:add_episode")
    b.button(text="✏️ Qism tahrirlash", callback_data="adm_series:edit_episode")
    b.button(text="🗑 Serial o'chirish", callback_data="adm_series:delete")
    b.button(text="📋 Seriallar ro'yxati", callback_data="adm_series:list")
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    b.adjust(2, 2, 2, 1)
    return b.as_markup()


def admin_categories_kb(categories) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Kategoriya qo'shish", callback_data="adm_cat:add")
    for c in categories:
        b.button(text=f"🗑 {c.name}", callback_data=f"adm_cat:del:{c.id}")
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    b.adjust(1)
    return b.as_markup()


def admin_channels_kb(channels) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Kanal qo'shish", callback_data="adm_ch:add")
    for c in channels:
        b.button(text=f"🗑 {c.title}", callback_data=f"adm_ch:del:{c.id}")
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    b.adjust(1)
    return b.as_markup()


def admin_premium_kb(plans) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    names = {"daily": "🗓 Kunlik", "weekly": "📆 Haftalik", "monthly": "📅 Oylik"}
    for p in plans:
        label = names.get(p.name, p.name)
        price_str = f"{p.price:,}".replace(",", " ") if p.price else "0"
        b.button(text=f"{label}: {p.duration_days} kun | {price_str} so'm ✏️", callback_data=f"adm_prem:manage:{p.id}")
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    b.adjust(1)
    return b.as_markup()


def admin_plan_manage_kb(plan_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⏳ Muddatini o'zgartirish", callback_data=f"adm_prem:edit_dur:{plan_id}")
    b.button(text="💵 Narxini o'zgartirish", callback_data=f"adm_prem:edit_pr:{plan_id}")
    b.button(text="🔙 Orqaga", callback_data="adm:premium")
    b.adjust(1)
    return b.as_markup()


def premium_choice_kb(prefix: str = "premchoice") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🆓 Bepul", callback_data=f"{prefix}:0")
    b.button(text="💎 Premium", callback_data=f"{prefix}:1")
    b.adjust(2)
    return b.as_markup()


def admin_promo_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Promo kod yaratish", callback_data="adm_promo:add")
    b.button(text="📋 Promo kodlar ro'yxati", callback_data="adm_promo:list")
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    b.adjust(1)
    return b.as_markup()


def admin_promo_list_kb(promos) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in promos:
        status = "✅" if p.is_active else "🚫"
        used = " (ishlatilgan)" if p.is_used else ""
        b.button(text=f"{status} {p.code}{used}", callback_data=f"adm_promo:view:{p.id}")
    b.button(text="🔙 Orqaga", callback_data="adm:promo")
    b.adjust(1)
    return b.as_markup()


def admin_promo_detail_kb(promo) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    toggle_text = "🚫 Noaktiv qilish" if promo.is_active else "✅ Aktiv qilish"
    b.button(text=toggle_text, callback_data=f"adm_promo:toggle:{promo.id}")
    b.button(text="🗑 O'chirish", callback_data=f"adm_promo:delete:{promo.id}")
    b.button(text="🔙 Orqaga", callback_data="adm_promo:list")
    b.adjust(1)
    return b.as_markup()


def plan_choice_kb(plans, prefix="adm_promo_plan") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    names = {"daily": "🗓 Kunlik", "weekly": "📆 Haftalik", "monthly": "📅 Oylik"}
    for p in plans:
        label = names.get(p.name, p.name)
        b.button(text=f"{label} ({p.duration_days} kun)", callback_data=f"{prefix}:{p.id}")
    b.adjust(1)
    return b.as_markup()


def category_choice_kb(categories, prefix="choosecat") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➖ Kategoriyasiz", callback_data=f"{prefix}:0")
    for c in categories:
        b.button(text=c.name, callback_data=f"{prefix}:{c.id}")
    b.adjust(2)
    return b.as_markup()


def skip_kb(callback_data: str = "skip") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⏭ O'tkazib yuborish", callback_data=callback_data)
    return b.as_markup()


def confirm_kb(yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Ha", callback_data=yes_cb)
    b.button(text="❌ Yo'q", callback_data=no_cb)
    b.adjust(2)
    return b.as_markup()


def movie_edit_fields_kb(movie_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    fields = [
        ("title", "📝 Nomi"),
        ("description", "📄 Tavsifi"),
        ("year", "📅 Yili"),
        ("quality", "🎞 Sifati"),
        ("language", "🗣 Tili"),
        ("is_premium", "💎 Maqomi (Premium/Bepul)"),
        ("cover_file_id", "🖼 Cover rasmi"),
        ("video_file_id", "🎬 Video fayli"),
    ]
    for field, label in fields:
        b.button(text=label, callback_data=f"adm_movie_edit_f:{movie_id}:{field}")
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    b.adjust(2)
    return b.as_markup()


def series_edit_fields_kb(series_id: int) -> InlineKeyboardMarkup:
    """Serial tahrirlash - qaysi maydonni o'zgartirish tanlash."""
    b = InlineKeyboardBuilder()
    fields = [
        ("title", "📝 Nomi"),
        ("description", "📄 Tavsifi"),
        ("year", "📅 Yili"),
        ("quality", "🎞 Sifati"),
        ("language", "🗣 Tili"),
        ("is_premium", "💎 Maqomi (Premium/Bepul)"),
        ("cover_file_id", "🖼 Cover rasmi"),
    ]
    for field, label in fields:
        b.button(text=label, callback_data=f"adm_series_edit_f:{series_id}:{field}")
    b.button(text="🎬 Qism videosini tahrirlash", callback_data=f"adm_series_edit_ep:{series_id}")
    b.button(text="🔙 Orqaga", callback_data="adm:series")
    b.adjust(2)
    return b.as_markup()


def after_episode_kb(series_id: int) -> InlineKeyboardMarkup:
    """Qism qo'shilgandan keyin chiquvchi keyboard: Yana qo'sh yoki Saqlash."""
    b = InlineKeyboardBuilder()
    b.button(text="➕ Yana qism qo'shish", callback_data=f"adm_series:more_ep:{series_id}")
    b.button(text="✅ Yuklash / Saqlash", callback_data=f"adm_series:finish:{series_id}")
    b.adjust(1)
    return b.as_markup()


def admin_settings_kb() -> InlineKeyboardMarkup:
    """Admin sozlamalar asosiy menyusi."""
    b = InlineKeyboardBuilder()
    b.button(text="⚙️ Premium sozlamalari", callback_data="adm_settings:premium")
    b.button(text="🔙 Orqaga", callback_data="adm:back")
    b.adjust(1)
    return b.as_markup()


def admin_premium_settings_kb() -> InlineKeyboardMarkup:
    """Premium sozlamalar menyusi."""
    b = InlineKeyboardBuilder()
    b.button(text="📝 To'lov xabarini tahrirlash", callback_data="adm_settings:edit_template")
    b.button(text="💳 1-karta raqamini o'zgartirish", callback_data="adm_settings:edit_card1")
    b.button(text="💳 2-karta raqamini o'zgartirish", callback_data="adm_settings:edit_card2")
    b.button(text="👤 Admin username o'zgartirish", callback_data="adm_settings:edit_admin_username")
    b.button(text="🔙 Orqaga", callback_data="adm:settings")
    b.adjust(1)
    return b.as_markup()


def order_confirm_kb(order_id: int) -> InlineKeyboardMarkup:
    """Premium buyurtmani tasdiqlash yoki rad etish."""
    b = InlineKeyboardBuilder()
    b.button(text="✅ Tasdiqlash", callback_data=f"adm_order:confirm:{order_id}")
    b.button(text="❌ Rad etish", callback_data=f"adm_order:reject:{order_id}")
    b.adjust(2)
    return b.as_markup()
