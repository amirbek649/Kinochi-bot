from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from ..database import requests as rq
from ..config import ADMIN_IDS
from ..keyboards.user_kb import (
    main_menu, cancel_kb, categories_kb, movies_list_kb, series_list_kb,
    episodes_kb, premium_menu_kb, subscribe_kb, plan_title,
)
from ..states.all_states import UserStates

user_router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ---------------------------------------------------------------------------
# YORDAMCHI FUNKSIYALAR
# ---------------------------------------------------------------------------

async def get_unsubscribed_channels(bot: Bot, user_id: int) -> list:
    """Foydalanuvchi obuna bo'lmagan majburiy kanallar ro'yxatini qaytaradi."""
    channels = await rq.get_channels()
    if not channels:
        return []

    unsubscribed = []
    for ch in channels:
        chat_ref = ch.username.strip()
        if not chat_ref.startswith("@") and not chat_ref.startswith("http"):
            chat_ref = "@" + chat_ref
        if chat_ref.startswith("http"):
            # https://t.me/xxx dan @xxx yasaymiz
            chat_ref = "@" + chat_ref.rstrip("/").split("/")[-1]
        try:
            member = await bot.get_chat_member(chat_id=chat_ref, user_id=user_id)
            if member.status in ("left", "kicked"):
                unsubscribed.append(ch)
        except Exception:
            # bot kanalga admin qilib qo'shilmagan yoki username noto'g'ri bo'lsa ham
            # foydalanuvchini bloklab qo'ymaslik uchun o'tkazib yuboramiz
            continue
    return unsubscribed


async def user_needs_subscription(bot: Bot, user_id: int) -> list:
    await rq.refresh_premium_status(user_id)
    user = await rq.get_user(user_id)
    if user and user.is_premium:
        return []
    return await get_unsubscribed_channels(bot, user_id)


async def deliver_movie(message: Message, bot: Bot, movie) -> None:
    caption = build_movie_caption(movie)
    if movie.cover_file_id:
        await message.answer_photo(movie.cover_file_id, caption=caption)
        await message.answer_video(movie.video_file_id)
    else:
        await message.answer_video(movie.video_file_id, caption=caption)


async def check_content_premium_access(user_id: int, is_premium_content: bool) -> bool:
    if not is_premium_content:
        return True
    return await rq.refresh_premium_status(user_id)


async def send_premium_required_message(target, plans):
    text = (
        "🔒 <b>Ushbu kino/serial faqat Premium obunachilar uchun!</b>\n\n"
        "Kinoni tomosha qilish va yuklab olish uchun Premium obunasini rasmiylashtiring."
    )
    kb = premium_menu_kb(plans, False)
    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb)
    elif isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=kb)
        await target.answer()


def build_movie_caption(movie) -> str:
    badge = " 💎 (Premium)" if getattr(movie, "is_premium", False) else ""
    lines = [f"🎬 <b>{movie.title}</b>{badge}", f"🔢 Kod: <code>{movie.code}</code>"]
    if movie.category:
        lines.append(f"📂 Kategoriya: {movie.category.name}")
    if movie.year:
        lines.append(f"📅 Yili: {movie.year}")
    if movie.quality:
        lines.append(f"🎞 Sifat: {movie.quality}")
    if movie.language:
        lines.append(f"🗣 Til: {movie.language}")
    if movie.description:
        lines.append(f"\n📄 {movie.description}")
    return "\n".join(lines)


def build_series_caption(series) -> str:
    badge = " 💎 (Premium)" if getattr(series, "is_premium", False) else ""
    lines = [f"📺 <b>{series.title}</b>{badge}", f"🔢 Kod: <code>{series.code}</code>"]
    if series.category:
        lines.append(f"📂 Kategoriya: {series.category.name}")
    if series.year:
        lines.append(f"📅 Yili: {series.year}")
    if series.description:
        lines.append(f"\n📄 {series.description}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# START / ASOSIY MENYU
# ---------------------------------------------------------------------------

@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await rq.get_or_create_user(message.from_user)
    await message.answer(
        "👋 Salom! <b>Kinochi</b> botiga xush kelibsiz!\n\n"
        "Bu yerda siz kino kodi orqali yoki nomi bo'yicha qidirib, "
        "kino va seriallarni bepul tomosha qilishingiz mumkin.",
        reply_markup=main_menu(is_admin(message.from_user.id)),
    )


@user_router.message(F.text == "🏠 Asosiy menyu")
async def go_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu(is_admin(message.from_user.id)))


@user_router.message(F.text == "❌ Bekor qilish")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Amal bekor qilindi.", reply_markup=main_menu(is_admin(message.from_user.id)))


@user_router.message(F.text == "ℹ️ Yordam")
async def help_message(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "🔢 <b>Kino kodi orqali</b> — kino kodini yuboring (masalan: 658)\n"
        "🎬 <b>Kino qidirish</b> — kino nomini yozing\n"
        "📂 <b>Kategoriyalar</b> — janr bo'yicha kinolarni ko'ring\n"
        "📺 <b>Seriallar</b> — seriallar va qismlarini tomosha qiling\n"
        "💎 <b>Premium</b> — majburiy obunasiz kino ko'rish imkoniyati\n"
        "🎁 <b>Promo kod</b> — promo kod orqali Premiumni faollashtiring"
    )


# ---------------------------------------------------------------------------
# KINO KODI ORQALI
# ---------------------------------------------------------------------------

@user_router.message(F.text == "🔢 Kino kodi orqali")
async def ask_movie_code(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_movie_code)
    await message.answer("🔢 Kino kodini yuboring (masalan: 658):", reply_markup=cancel_kb())


@user_router.message(UserStates.waiting_movie_code)
async def receive_movie_code(message: Message, state: FSMContext, bot: Bot):
    code = message.text.strip()
    movie = await rq.get_movie_by_code(code)
    if not movie:
        await message.answer("❌ Bu kodga tegishli kino topilmadi. Qaytadan urinib ko'ring.")
        return

    await state.clear()
    if movie.is_premium and not await check_content_premium_access(message.from_user.id, True):
        plans = await rq.get_plans()
        await send_premium_required_message(message, plans)
        return

    unsub = await user_needs_subscription(bot, message.from_user.id)
    if unsub:
        await message.answer(
            "📢 Kinoni olishdan oldin quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscribe_kb(unsub, "movie", movie.id),
        )
        return

    await deliver_movie(message, bot, movie)
    await message.answer("🏠 Asosiy menyu:", reply_markup=main_menu(is_admin(message.from_user.id)))


# ---------------------------------------------------------------------------
# KINO QIDIRISH
# ---------------------------------------------------------------------------

@user_router.message(F.text == "🎬 Kino qidirish")
async def ask_search_query(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_search_query)
    await message.answer("🔎 Kino nomini yozing:", reply_markup=cancel_kb())


@user_router.message(UserStates.waiting_search_query)
async def receive_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    movies = await rq.search_movies_by_title(query)
    await state.clear()
    if not movies:
        await message.answer(
            "❌ Hech narsa topilmadi.", reply_markup=main_menu(is_admin(message.from_user.id))
        )
        return
    await message.answer(
        f"🔎 <b>{query}</b> bo'yicha natijalar:",
        reply_markup=movies_list_kb(movies),
    )


@user_router.callback_query(F.data.startswith("getmovie:"))
async def cb_get_movie(callback: CallbackQuery, bot: Bot):
    movie_id = int(callback.data.split(":")[1])
    movie = await rq.get_movie_by_id(movie_id)
    if not movie:
        await callback.answer("❌ Kino topilmadi.", show_alert=True)
        return

    if movie.is_premium and not await check_content_premium_access(callback.from_user.id, True):
        plans = await rq.get_plans()
        await send_premium_required_message(callback, plans)
        return

    unsub = await user_needs_subscription(bot, callback.from_user.id)
    if unsub:
        await callback.message.answer(
            "📢 Kinoni olishdan oldin quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscribe_kb(unsub, "movie", movie.id),
        )
        await callback.answer()
        return

    await deliver_movie(callback.message, bot, movie)
    await callback.answer()


# ---------------------------------------------------------------------------
# KATEGORIYALAR
# ---------------------------------------------------------------------------

@user_router.message(F.text == "📂 Kategoriyalar")
async def show_categories(message: Message):
    categories = await rq.get_categories()
    if not categories:
        await message.answer("❌ Hozircha kategoriyalar mavjud emas.")
        return
    await message.answer("📂 Kategoriyani tanlang:", reply_markup=categories_kb(categories))


@user_router.callback_query(F.data.startswith("cat:"))
async def cb_show_category_movies(callback: CallbackQuery):
    category_id = int(callback.data.split(":")[1])
    category = await rq.get_category(category_id)
    movies = await rq.get_movies_by_category(category_id)
    if not movies:
        await callback.answer("❌ Bu kategoriyada hali kino yo'q.", show_alert=True)
        return
    await callback.message.answer(
        f"📂 <b>{category.name}</b> kategoriyasidagi kinolar:",
        reply_markup=movies_list_kb(movies),
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# SERIALLAR
# ---------------------------------------------------------------------------

@user_router.message(F.text == "📺 Seriallar")
async def show_series(message: Message):
    series_list = await rq.get_all_series()
    if not series_list:
        await message.answer("❌ Hozircha seriallar mavjud emas.")
        return
    await message.answer("📺 Serialni tanlang:", reply_markup=series_list_kb(series_list))


@user_router.callback_query(F.data.startswith("getseries:"))
async def cb_show_series_episodes(callback: CallbackQuery):
    series_id = int(callback.data.split(":")[1])
    series = await rq.get_series_by_id(series_id)
    if not series:
        await callback.answer("❌ Serial topilmadi.", show_alert=True)
        return
    episodes = await rq.get_episodes_by_series(series_id)
    if not episodes:
        await callback.answer("❌ Bu serialda hali qismlar yo'q.", show_alert=True)
        return

    caption = build_series_caption(series)
    if series.cover_file_id:
        await callback.message.answer_photo(series.cover_file_id, caption=caption)
    else:
        await callback.message.answer(caption)

    await callback.message.answer("📺 Qismni tanlang:", reply_markup=episodes_kb(episodes))
    await callback.answer()


@user_router.callback_query(F.data.startswith("getepisode:"))
async def cb_get_episode(callback: CallbackQuery, bot: Bot):
    episode_id = int(callback.data.split(":")[1])
    episode = await rq.get_episode_by_id(episode_id)
    if not episode:
        await callback.answer("❌ Qism topilmadi.", show_alert=True)
        return

    if episode.series.is_premium and not await check_content_premium_access(callback.from_user.id, True):
        plans = await rq.get_plans()
        await send_premium_required_message(callback, plans)
        return

    unsub = await user_needs_subscription(bot, callback.from_user.id)
    if unsub:
        await callback.message.answer(
            "📢 Qismni olishdan oldin quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscribe_kb(unsub, "episode", episode.id),
        )
        await callback.answer()
        return

    await callback.message.answer_video(
        episode.video_file_id,
        caption=f"📺 {episode.series.title} — {episode.episode_number}-qism",
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# OBUNANI TEKSHIRISH
# ---------------------------------------------------------------------------

@user_router.callback_query(F.data.startswith("checksub:"))
async def cb_check_subscription(callback: CallbackQuery, bot: Bot):
    _, pending_type, ref_id = callback.data.split(":")
    ref_id = int(ref_id)

    unsub = await user_needs_subscription(bot, callback.from_user.id)
    if unsub:
        await callback.answer("❌ Siz hali barcha kanallarga obuna bo'lmagansiz!", show_alert=True)
        return

    await callback.answer("✅ Obuna tasdiqlandi!")
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if pending_type == "movie":
        movie = await rq.get_movie_by_id(ref_id)
        if movie:
            if movie.is_premium and not await check_content_premium_access(callback.from_user.id, True):
                plans = await rq.get_plans()
                await send_premium_required_message(callback, plans)
                return
            await deliver_movie(callback.message, bot, movie)
    elif pending_type == "episode":
        episode = await rq.get_episode_by_id(ref_id)
        if episode:
            if episode.series.is_premium and not await check_content_premium_access(callback.from_user.id, True):
                plans = await rq.get_plans()
                await send_premium_required_message(callback, plans)
                return
            await callback.message.answer_video(
                episode.video_file_id,
                caption=f"📺 {episode.series.title} — {episode.episode_number}-qism",
            )


# ---------------------------------------------------------------------------
# PREMIUM / PROMO KOD
# ---------------------------------------------------------------------------

@user_router.message(F.text == "💎 Premium")
async def show_premium(message: Message):
    await rq.refresh_premium_status(message.from_user.id)
    user = await rq.get_user(message.from_user.id)
    plans = await rq.get_plans()

    if user and user.is_premium and user.premium_until:
        status = (
            f"✅ Sizda hozir <b>Premium</b> faol!\n"
            f"⏳ Muddati: {user.premium_until.strftime('%d.%m.%Y %H:%M')} gacha\n\n"
        )
    else:
        status = "🚫 Sizda hozircha Premium mavjud emas.\n\n"

    text = (
        status
        + "💎 <b>Premium imkoniyatlari:</b>\n"
        "• Majburiy obunasiz kino/serial ko'rish\n"
        "• Eksklyuziv Premium kinolarni yuklash va tomosha qilish\n\n"
        "📌 Mavjud tariflar va narxlar:\n"
    )
    if not plans:
        text += "— hozircha tarif belgilanmagan"
    else:
        for p in plans:
            price_val = getattr(p, "price", 0) or 0
            price_str = f"{price_val:,}".replace(",", " ")
            text += f"• {plan_title(p.name)} ({p.duration_days} kun) — <b>{price_str} so'm</b>\n"

    await message.answer(text, reply_markup=premium_menu_kb(plans, bool(user and user.is_premium)))


@user_router.callback_query(F.data == "enter_promo")
async def cb_enter_promo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.waiting_promo_code)
    await callback.message.answer("🎁 Promo kodni kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@user_router.callback_query(F.data.startswith("noop:"))
async def cb_noop(callback: CallbackQuery):
    await callback.answer()


@user_router.message(F.text == "🎁 Promo kod")
async def ask_promo_directly(message: Message, state: FSMContext):
    await state.set_state(UserStates.waiting_promo_code)
    await message.answer("🎁 Promo kodni kiriting:", reply_markup=cancel_kb())


@user_router.message(UserStates.waiting_promo_code)
async def receive_promo_code(message: Message, state: FSMContext):
    code = message.text.strip()
    ok, text, days = await rq.use_promo(code, message.from_user.id)
    await state.clear()

    if ok and days:
        until = await rq.activate_premium(message.from_user.id, days)
        text += f"\n💎 Premium muddati: {until.strftime('%d.%m.%Y %H:%M')} gacha"

    await message.answer(text, reply_markup=main_menu(is_admin(message.from_user.id)))
