from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from ..database import requests as rq
from ..config import ADMIN_IDS
from ..filters.admin_filter import IsAdmin
from ..keyboards.user_kb import main_menu, cancel_kb, plan_title
from ..keyboards.admin_kb import (
    admin_main_kb, back_to_admin_kb, admin_movies_kb, admin_series_kb,
    admin_categories_kb, admin_channels_kb, admin_premium_kb, admin_promo_kb,
    admin_promo_list_kb, admin_promo_detail_kb, plan_choice_kb, category_choice_kb,
    skip_kb, movie_edit_fields_kb, premium_choice_kb, admin_plan_manage_kb,
    series_edit_fields_kb, after_episode_kb,
    admin_settings_kb, admin_premium_settings_kb, order_confirm_kb,
)
from ..states.all_states import (
    AdminMovieAdd, AdminMovieEdit, AdminMovieDelete, AdminMovieSearch,
    AdminSeriesAdd, AdminSeriesDelete, AdminEpisodeAdd,
    AdminSeriesEdit, AdminEpisodeEdit,
    AdminCategory, AdminChannel, AdminPremium, AdminPromo, AdminBroadcast,
    AdminSettings,
)

admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())


async def safe_edit(callback: CallbackQuery, text: str, kb=None) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=kb)


# ---------------------------------------------------------------------------
# ADMIN PANELGA KIRISH
# ---------------------------------------------------------------------------

@admin_router.message(F.text == "⚙️ Admin panel")
@admin_router.message(Command("admin"))
async def open_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⚙️ <b>Admin panel</b>:", reply_markup=admin_main_kb())


@admin_router.callback_query(F.data == "adm:back")
async def cb_back_to_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(callback, "⚙️ <b>Admin panel</b>:", admin_main_kb())
    await callback.answer()


# ---------------------------------------------------------------------------
# KINOLAR BO'LIMI
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm:movies")
async def cb_admin_movies(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(callback, "🎬 <b>Kinolar</b> bo'limi:", admin_movies_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "adm_movie:add")
async def cb_add_movie_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminMovieAdd.code)
    await callback.message.answer("🔢 Kino kodini kiriting (masalan: 658):", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminMovieAdd.code)
async def receive_movie_code(message: Message, state: FSMContext):
    code = message.text.strip()
    if await rq.get_movie_by_code(code):
        await message.answer("❌ Bu kod band. Boshqa kod kiriting.")
        return
    await state.update_data(code=code)
    await state.set_state(AdminMovieAdd.title)
    await message.answer("📝 Kino nomini kiriting:")


@admin_router.message(AdminMovieAdd.title)
async def receive_movie_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminMovieAdd.category)
    cats = await rq.get_categories()
    await message.answer("📂 Kategoriyani tanlang:", reply_markup=category_choice_kb(cats, prefix="moviecat"))


@admin_router.callback_query(F.data.startswith("moviecat:"), AdminMovieAdd.category)
async def receive_movie_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=(cat_id or None))
    await state.set_state(AdminMovieAdd.description)
    await callback.message.answer(
        "📄 Tavsifni kiriting (yoki o'tkazib yuborish uchun tugmani bosing):",
        reply_markup=skip_kb("skip_movie_desc"),
    )
    await callback.answer()


@admin_router.callback_query(F.data == "skip_movie_desc", AdminMovieAdd.description)
async def skip_movie_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description=None)
    await state.set_state(AdminMovieAdd.year)
    await callback.message.answer("📅 Kino yilini kiriting (masalan: 2024):")
    await callback.answer()


@admin_router.message(AdminMovieAdd.description)
async def receive_movie_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AdminMovieAdd.year)
    await message.answer("📅 Kino yilini kiriting (masalan: 2024):")


@admin_router.message(AdminMovieAdd.year)
async def receive_movie_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text.strip())
    await state.set_state(AdminMovieAdd.quality)
    await message.answer("🎞 Sifatini kiriting (masalan: HD, 1080p):")


@admin_router.message(AdminMovieAdd.quality)
async def receive_movie_quality(message: Message, state: FSMContext):
    await state.update_data(quality=message.text.strip())
    await state.set_state(AdminMovieAdd.language)
    await message.answer("🗣 Tilini kiriting (masalan: O'zbek tilida):")


@admin_router.message(AdminMovieAdd.language)
async def receive_movie_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text.strip())
    await state.set_state(AdminMovieAdd.is_premium)
    await message.answer(
        "💎 Ushbu kino turini tanlang:",
        reply_markup=premium_choice_kb(prefix="movieprem"),
    )


@admin_router.callback_query(F.data.startswith("movieprem:"), AdminMovieAdd.is_premium)
async def receive_movie_premium(callback: CallbackQuery, state: FSMContext):
    is_prem = bool(int(callback.data.split(":")[1]))
    await state.update_data(is_premium=is_prem)
    await state.set_state(AdminMovieAdd.cover)
    await callback.message.answer(
        "🖼 Cover rasmini yuboring (yoki o'tkazib yuborish uchun tugmani bosing):",
        reply_markup=skip_kb("skip_movie_cover"),
    )
    await callback.answer()


@admin_router.callback_query(F.data == "skip_movie_cover", AdminMovieAdd.cover)
async def skip_movie_cover(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cover_file_id=None)
    await state.set_state(AdminMovieAdd.video)
    await callback.message.answer("🎬 Video faylni yuboring:")
    await callback.answer()


@admin_router.message(AdminMovieAdd.cover, F.photo)
async def receive_movie_cover(message: Message, state: FSMContext):
    await state.update_data(cover_file_id=message.photo[-1].file_id)
    await state.set_state(AdminMovieAdd.video)
    await message.answer("🎬 Video faylni yuboring:")


@admin_router.message(AdminMovieAdd.cover)
async def receive_movie_cover_invalid(message: Message):
    await message.answer("❌ Iltimos rasm yuboring yoki o'tkazib yuborish tugmasini bosing.")


@admin_router.message(AdminMovieAdd.video, F.video)
async def receive_movie_video(message: Message, state: FSMContext):
    data = await state.get_data()
    movie = await rq.add_movie(
        code=data["code"],
        title=data["title"],
        category_id=data.get("category_id"),
        description=data.get("description"),
        year=data.get("year"),
        quality=data.get("quality"),
        language=data.get("language"),
        is_premium=data.get("is_premium", False),
        cover_file_id=data.get("cover_file_id"),
        video_file_id=message.video.file_id,
    )
    await state.clear()
    type_badge = "💎 Premium" if movie.is_premium else "🆓 Bepul"
    await message.answer(
        f"✅ Kino qo'shildi!\n\n🎬 {movie.title}\n🔢 Kod: {movie.code}\n📌 Tur: {type_badge}",
        reply_markup=main_menu(True),
    )
    await message.answer("🎬 Kinolar bo'limi:", reply_markup=admin_movies_kb())


@admin_router.message(AdminMovieAdd.video)
async def receive_movie_video_invalid(message: Message):
    await message.answer("❌ Iltimos video fayl yuboring.")


# --- Kino qidirish (admin) ---

@admin_router.callback_query(F.data == "adm_movie:search")
async def cb_admin_movie_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminMovieSearch.query)
    await callback.message.answer("🔍 Qidiruv uchun kino nomini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminMovieSearch.query)
async def receive_admin_movie_search(message: Message, state: FSMContext):
    movies = await rq.search_movies_by_title(message.text.strip())
    await state.clear()
    if not movies:
        await message.answer("❌ Hech narsa topilmadi.", reply_markup=main_menu(True))
        return
    text = "\n".join(f"🎬 {m.title} — kod: {m.code}" for m in movies)
    await message.answer(f"🔍 Natijalar:\n\n{text}", reply_markup=main_menu(True))


# --- Kino o'chirish ---

@admin_router.callback_query(F.data == "adm_movie:delete")
async def cb_admin_movie_delete_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminMovieDelete.choose_code)
    await callback.message.answer("🗑 O'chirish uchun kino kodini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminMovieDelete.choose_code)
async def receive_movie_delete_code(message: Message, state: FSMContext):
    movie = await rq.get_movie_by_code(message.text.strip())
    if not movie:
        await message.answer("❌ Bunday kodli kino topilmadi.")
        return
    await state.clear()
    await rq.delete_movie(movie.id)
    await message.answer(f"🗑 '{movie.title}' ({movie.code}) o'chirildi.", reply_markup=main_menu(True))


# --- Kino tahrirlash ---

@admin_router.callback_query(F.data == "adm_movie:edit")
async def cb_admin_movie_edit_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminMovieEdit.choose_code)
    await callback.message.answer("✏️ Tahrirlash uchun kino kodini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminMovieEdit.choose_code)
async def receive_movie_edit_code(message: Message, state: FSMContext):
    movie = await rq.get_movie_by_code(message.text.strip())
    if not movie:
        await message.answer("❌ Bunday kodli kino topilmadi.")
        return
    await state.clear()
    await message.answer(
        f"✏️ '{movie.title}' ({movie.code})\nQaysi maydonni tahrirlaysiz?",
        reply_markup=movie_edit_fields_kb(movie.id),
    )


@admin_router.callback_query(F.data.startswith("adm_movie_edit_f:"))
async def cb_choose_edit_field(callback: CallbackQuery, state: FSMContext):
    _, movie_id, field = callback.data.split(":")
    movie_id = int(movie_id)
    if field == "is_premium":
        await state.update_data(movie_id=movie_id, field=field)
        await state.set_state(AdminMovieEdit.new_value)
        await callback.message.answer(
            "💎 Kinoning yangi maqomini tanlang:",
            reply_markup=premium_choice_kb(prefix="editmovieprem"),
        )
        await callback.answer()
        return
    await state.update_data(movie_id=movie_id, field=field)
    await state.set_state(AdminMovieEdit.new_value)
    field_names = {
        "title": "📝 Yangi nomni", "description": "📄 Yangi tavsifni", "year": "📅 Yangi yilni",
        "quality": "🎞 Yangi sifatni", "language": "🗣 Yangi tilni",
        "cover_file_id": "🖼 Yangi cover rasmini", "video_file_id": "🎬 Yangi video faylni",
    }
    prompt = field_names.get(field, "Yangi qiymatni")
    await callback.message.answer(f"{prompt} yuboring:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("editmovieprem:"), AdminMovieEdit.new_value)
async def receive_edit_movie_premium(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_prem = bool(int(callback.data.split(":")[1]))
    await rq.update_movie_field(data["movie_id"], "is_premium", is_prem)
    await state.clear()
    await callback.message.answer("✅ Kino maqomi yangilandi.", reply_markup=main_menu(True))
    await callback.answer()


@admin_router.message(AdminMovieEdit.new_value, F.photo)
async def receive_edit_value_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("field") != "cover_file_id":
        await message.answer("❌ Bu maydon uchun rasm emas, matn/qiymat kerak.")
        return
    await rq.update_movie_field(data["movie_id"], "cover_file_id", message.photo[-1].file_id)
    await state.clear()
    await message.answer("✅ Cover rasmi yangilandi.", reply_markup=main_menu(True))


@admin_router.message(AdminMovieEdit.new_value, F.video)
async def receive_edit_value_video(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("field") != "video_file_id":
        await message.answer("❌ Bu maydon uchun video emas, matn kerak.")
        return
    await rq.update_movie_field(data["movie_id"], "video_file_id", message.video.file_id)
    await state.clear()
    await message.answer("✅ Video fayl yangilandi.", reply_markup=main_menu(True))


@admin_router.message(AdminMovieEdit.new_value)
async def receive_edit_value_text(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")
    if field in ("cover_file_id", "video_file_id"):
        await message.answer("❌ Iltimos mos fayl (rasm/video) yuboring.")
        return
    await rq.update_movie_field(data["movie_id"], field, message.text.strip())
    await state.clear()
    await message.answer("✅ Yangilandi.", reply_markup=main_menu(True))


# ---------------------------------------------------------------------------
# SERIALLAR BO'LIMI
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm:series")
async def cb_admin_series(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(callback, "📺 <b>Seriallar</b> bo'limi:", admin_series_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "adm_series:add")
async def cb_add_series_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSeriesAdd.code)
    await callback.message.answer("🔢 Serial kodini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminSeriesAdd.code)
async def receive_series_code(message: Message, state: FSMContext):
    code = message.text.strip()
    if await rq.get_series_by_code(code):
        await message.answer("❌ Bu kod band. Boshqa kod kiriting.")
        return
    await state.update_data(code=code)
    await state.set_state(AdminSeriesAdd.title)
    await message.answer("📝 Serial nomini kiriting:")


@admin_router.message(AdminSeriesAdd.title)
async def receive_series_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminSeriesAdd.category)
    cats = await rq.get_categories()
    await message.answer("📂 Kategoriyani tanlang:", reply_markup=category_choice_kb(cats, prefix="seriescat"))


@admin_router.callback_query(F.data.startswith("seriescat:"), AdminSeriesAdd.category)
async def receive_series_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=(cat_id or None))
    await state.set_state(AdminSeriesAdd.description)
    await callback.message.answer(
        "📄 Tavsifni kiriting (yoki o'tkazib yuborish):", reply_markup=skip_kb("skip_series_desc")
    )
    await callback.answer()


@admin_router.callback_query(F.data == "skip_series_desc", AdminSeriesAdd.description)
async def skip_series_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description=None)
    await state.set_state(AdminSeriesAdd.year)
    await callback.message.answer("📅 Yilini kiriting:")
    await callback.answer()


@admin_router.message(AdminSeriesAdd.description)
async def receive_series_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AdminSeriesAdd.year)
    await message.answer("📅 Yilini kiriting:")


@admin_router.message(AdminSeriesAdd.year)
async def receive_series_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text.strip())
    await state.set_state(AdminSeriesAdd.quality)
    await message.answer("🎞 Sifatini kiriting:")


@admin_router.message(AdminSeriesAdd.quality)
async def receive_series_quality(message: Message, state: FSMContext):
    await state.update_data(quality=message.text.strip())
    await state.set_state(AdminSeriesAdd.language)
    await message.answer("🗣 Tilini kiriting:")


@admin_router.message(AdminSeriesAdd.language)
async def receive_series_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text.strip())
    await state.set_state(AdminSeriesAdd.is_premium)
    await message.answer(
        "💎 Ushbu serial turini tanlang:",
        reply_markup=premium_choice_kb(prefix="seriesprem"),
    )


@admin_router.callback_query(F.data.startswith("seriesprem:"), AdminSeriesAdd.is_premium)
async def receive_series_premium(callback: CallbackQuery, state: FSMContext):
    is_prem = bool(int(callback.data.split(":")[1]))
    await state.update_data(is_premium=is_prem)
    await state.set_state(AdminSeriesAdd.cover)
    await callback.message.answer(
        "🖼 Cover rasmini yuboring (yoki o'tkazib yuborish):", reply_markup=skip_kb("skip_series_cover")
    )
    await callback.answer()


async def _finalize_series(state: FSMContext, cover_file_id: str | None):
    data = await state.get_data()
    return await rq.add_series(
        code=data["code"], title=data["title"], category_id=data.get("category_id"),
        description=data.get("description"), year=data.get("year"), quality=data.get("quality"),
        language=data.get("language"), is_premium=data.get("is_premium", False),
        cover_file_id=cover_file_id,
    )


@admin_router.callback_query(F.data == "skip_series_cover", AdminSeriesAdd.cover)
async def skip_series_cover(callback: CallbackQuery, state: FSMContext):
    series = await _finalize_series(state, None)
    await state.update_data(series_id=series.id, series_title=series.title, next_episode=1)
    await state.set_state(AdminSeriesAdd.episode_video)
    await callback.message.answer(
        f"✅ Serial qo'shildi!\n\n📺 <b>{series.title}</b>\n🔢 Kod: {series.code}\n\n"
        f"🎬 Endi <b>1-qism</b> video faylini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@admin_router.message(AdminSeriesAdd.cover, F.photo)
async def receive_series_cover(message: Message, state: FSMContext):
    series = await _finalize_series(state, message.photo[-1].file_id)
    await state.update_data(series_id=series.id, series_title=series.title, next_episode=1)
    await state.set_state(AdminSeriesAdd.episode_video)
    await message.answer(
        f"✅ Serial qo'shildi!\n\n📺 <b>{series.title}</b>\n🔢 Kod: {series.code}\n\n"
        f"🎬 Endi <b>1-qism</b> video faylini yuboring:",
        reply_markup=cancel_kb(),
    )


@admin_router.message(AdminSeriesAdd.cover)
async def receive_series_cover_invalid(message: Message):
    await message.answer("❌ Iltimos rasm yuboring yoki o'tkazib yuborish tugmasini bosing.")


@admin_router.message(AdminSeriesAdd.episode_video, F.video)
async def receive_series_first_episode(message: Message, state: FSMContext):
    """Serial qo'shish jarayonida ketma-ket qism videolarini qabul qiladi."""
    data = await state.get_data()
    series_id = data["series_id"]
    series_title = data["series_title"]
    ep_num = data.get("next_episode", 1)

    # Duplicate episode tekshirish
    existing = await rq.get_episode_by_series_and_number(series_id, ep_num)
    if existing:
        await message.answer(
            f"⚠️ {ep_num}-qism allaqachon mavjud. Yana qism qo'shish tugmasini bosib davom eting.",
            reply_markup=after_episode_kb(series_id),
        )
        return

    await rq.add_episode(series_id, ep_num, message.video.file_id)
    await state.update_data(next_episode=ep_num + 1)
    await message.answer(
        f"✅ <b>{ep_num}-qism</b> saqlandi!\n\n"
        f"📺 {series_title} — jami {ep_num} ta qism\n\n"
        "Yana qism qo'shasizmi yoki yakunlaysizmi?",
        reply_markup=after_episode_kb(series_id),
    )


@admin_router.message(AdminSeriesAdd.episode_video)
async def receive_series_episode_invalid(message: Message):
    await message.answer("❌ Iltimos video fayl yuboring.")


@admin_router.callback_query(F.data.startswith("adm_series:more_ep:"))
async def cb_more_episode(callback: CallbackQuery, state: FSMContext):
    """Yana qism qo'shish — keyingi qism raqami bilan davom etadi."""
    series_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    ep_num = data.get("next_episode", 1)
    await state.set_state(AdminSeriesAdd.episode_video)
    await callback.message.answer(
        f"🎬 <b>{ep_num}-qism</b> video faylini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_series:finish:"))
async def cb_finish_series(callback: CallbackQuery, state: FSMContext):
    """Barcha qismlar qo'shildi — jarayonni yakunlash."""
    data = await state.get_data()
    series_title = data.get("series_title", "Serial")
    ep_num = data.get("next_episode", 1) - 1
    await state.clear()
    await callback.message.answer(
        f"✅ <b>{series_title}</b> seriali muvaffaqiyatli saqlandi!\n\n"
        f"📊 Jami qismlar: <b>{ep_num}</b> ta",
        reply_markup=main_menu(True),
    )
    await callback.message.answer("📺 Seriallar bo'limi:", reply_markup=admin_series_kb())
    await callback.answer()




# --- Qism qo'shish ---

@admin_router.callback_query(F.data == "adm_series:add_episode")
async def cb_add_episode_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminEpisodeAdd.series_code)
    await callback.message.answer("🔢 Qism qo'shmoqchi bo'lgan serial kodini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminEpisodeAdd.series_code)
async def receive_episode_series_code(message: Message, state: FSMContext):
    series = await rq.get_series_by_code(message.text.strip())
    if not series:
        await message.answer("❌ Bunday kodli serial topilmadi.")
        return
    await state.update_data(series_id=series.id, series_title=series.title)
    await state.set_state(AdminEpisodeAdd.episode_number)
    await message.answer("🔢 Qism raqamini kiriting (masalan: 1):")


@admin_router.message(AdminEpisodeAdd.episode_number)
async def receive_episode_number(message: Message, state: FSMContext):
    try:
        num = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Iltimos butun son kiriting.")
        return
    await state.update_data(episode_number=num)
    await state.set_state(AdminEpisodeAdd.video)
    await message.answer("🎬 Qism video faylini yuboring:")


@admin_router.message(AdminEpisodeAdd.video, F.video)
async def receive_episode_video(message: Message, state: FSMContext):
    data = await state.get_data()
    ep = await rq.add_episode(data["series_id"], data["episode_number"], message.video.file_id)
    await state.clear()
    await message.answer(
        f"✅ Qism qo'shildi!\n\n📺 {data['series_title']} — {ep.episode_number}-qism",
        reply_markup=main_menu(True),
    )


@admin_router.message(AdminEpisodeAdd.video)
async def receive_episode_video_invalid(message: Message):
    await message.answer("❌ Iltimos video fayl yuboring.")


# --- Seriallar ro'yxati / o'chirish ---

@admin_router.callback_query(F.data == "adm_series:list")
async def cb_series_list(callback: CallbackQuery):
    series_list = await rq.get_all_series()
    if not series_list:
        await callback.answer("❌ Hozircha seriallar yo'q.", show_alert=True)
        return
    text = "\n".join(f"📺 {s.title} — kod: {s.code}" for s in series_list)
    await callback.message.answer(f"📋 Seriallar ro'yxati:\n\n{text}")
    await callback.answer()


@admin_router.callback_query(F.data == "adm_series:delete")
async def cb_series_delete_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSeriesDelete.choose_code)
    await callback.message.answer("🗑 O'chirish uchun serial kodini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminSeriesDelete.choose_code)
async def receive_series_delete_code(message: Message, state: FSMContext):
    series = await rq.get_series_by_code(message.text.strip())
    if not series:
        await message.answer("❌ Bunday kodli serial topilmadi.")
        return
    await state.clear()
    await rq.delete_series(series.id)
    await message.answer(
        f"🗑 '{series.title}' ({series.code}) barcha qismlari bilan o'chirildi.", reply_markup=main_menu(True)
    )


# ---------------------------------------------------------------------------
# KATEGORIYALAR BO'LIMI
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm:categories")
async def cb_admin_categories(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    cats = await rq.get_categories()
    await safe_edit(
        callback,
        "📂 <b>Kategoriyalar</b> bo'limi:\nO'chirish uchun kategoriya tugmasini bosing.",
        admin_categories_kb(cats),
    )
    await callback.answer()


@admin_router.callback_query(F.data == "adm_cat:add")
async def cb_add_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminCategory.add_name)
    await callback.message.answer("📂 Yangi kategoriya nomini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminCategory.add_name)
async def receive_category_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await rq.add_category(name)
    await state.clear()
    cats = await rq.get_categories()
    await message.answer(f"✅ '{name}' kategoriyasi qo'shildi.", reply_markup=main_menu(True))
    await message.answer("📂 Kategoriyalar:", reply_markup=admin_categories_kb(cats))


@admin_router.callback_query(F.data.startswith("adm_cat:del:"))
async def cb_delete_category(callback: CallbackQuery):
    cat_id = int(callback.data.split(":")[2])
    await rq.delete_category(cat_id)
    cats = await rq.get_categories()
    await safe_edit(callback, "📂 <b>Kategoriyalar</b> bo'limi:", admin_categories_kb(cats))
    await callback.answer("🗑 O'chirildi")


# ---------------------------------------------------------------------------
# MAJBURIY OBUNA
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm:channels")
async def cb_admin_channels(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    channels = await rq.get_channels()
    await safe_edit(
        callback,
        "📢 <b>Majburiy obuna</b> kanallari:\nO'chirish uchun kanal tugmasini bosing.",
        admin_channels_kb(channels),
    )
    await callback.answer()


@admin_router.callback_query(F.data == "adm_ch:add")
async def cb_add_channel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminChannel.title)
    await callback.message.answer("📢 Kanal nomini kiriting (masalan: Kinochi Rasmiy kanali):", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminChannel.title)
async def receive_channel_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminChannel.username)
    await message.answer(
        "📢 Kanal username yoki linkini kiriting (masalan: @kinochi yoki https://t.me/kinochi):"
    )


@admin_router.message(AdminChannel.username)
async def receive_channel_username(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.add_channel(data["title"], message.text.strip())
    await state.clear()
    channels = await rq.get_channels()
    await message.answer(f"✅ '{data['title']}' kanali qo'shildi.", reply_markup=main_menu(True))
    await message.answer("📢 Majburiy obuna kanallari:", reply_markup=admin_channels_kb(channels))


@admin_router.callback_query(F.data.startswith("adm_ch:del:"))
async def cb_delete_channel(callback: CallbackQuery):
    ch_id = int(callback.data.split(":")[2])
    await rq.delete_channel(ch_id)
    channels = await rq.get_channels()
    await safe_edit(callback, "📢 <b>Majburiy obuna</b> kanallari:", admin_channels_kb(channels))
    await callback.answer("🗑 O'chirildi")


# ---------------------------------------------------------------------------
# PREMIUM TARIFLARI
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm:premium")
async def cb_admin_premium(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await rq.ensure_default_plans()
    plans = await rq.get_plans()
    await safe_edit(
        callback,
        "💎 <b>Premium tariflari</b>\nO'zgartirish uchun kerakli tarif tugmasini bosing:",
        admin_premium_kb(plans),
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_prem:manage:"))
async def cb_manage_premium_plan(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split(":")[2])
    plan = await rq.get_plan(plan_id)
    if not plan:
        await callback.answer("❌ Topilmadi", show_alert=True)
        return
    price_str = f"{plan.price:,}".replace(",", " ") if plan.price else "0"
    text = (
        f"💎 <b>{plan_title(plan.name)} tarifi</b>\n\n"
        f"⏳ Muddat: <b>{plan.duration_days} kun</b>\n"
        f"💵 Narx: <b>{price_str} so'm</b>\n\n"
        "Qaysi ma'lumotni o'zgartirmoqchisiz?"
    )
    await safe_edit(callback, text, admin_plan_manage_kb(plan.id))
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_prem:edit_dur:"))
async def cb_edit_plan_duration(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split(":")[2])
    plan = await rq.get_plan(plan_id)
    if not plan:
        await callback.answer("❌ Topilmadi", show_alert=True)
        return
    await state.update_data(plan_name=plan.name)
    await state.set_state(AdminPremium.duration)
    await callback.message.answer(
        f"💎 '{plan_title(plan.name)}' tarifi uchun necha kunlik muddat berilsin? (butun son kiriting):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_prem:edit_pr:"))
async def cb_edit_plan_price(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split(":")[2])
    plan = await rq.get_plan(plan_id)
    if not plan:
        await callback.answer("❌ Topilmadi", show_alert=True)
        return
    await state.update_data(plan_name=plan.name)
    await state.set_state(AdminPremium.price)
    await callback.message.answer(
        f"💵 '{plan_title(plan.name)}' tarifi narxini kiriting (so'mda, masalan: 25000):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@admin_router.message(AdminPremium.duration)
async def receive_premium_duration(message: Message, state: FSMContext):
    try:
        days = int(message.text.strip())
        if days <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Iltimos musbat butun son kiriting.")
        return
    data = await state.get_data()
    await rq.set_plan_duration(data["plan_name"], days)
    await state.clear()
    plans = await rq.get_plans()
    await message.answer("✅ Tarif muddati yangilandi.", reply_markup=main_menu(True))
    await message.answer("💎 Premium tariflari:", reply_markup=admin_premium_kb(plans))


@admin_router.message(AdminPremium.price)
async def receive_premium_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.strip())
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Iltimos noldan katta musbat butun son kiriting (masalan: 25000).")
        return
    data = await state.get_data()
    await rq.set_plan_price(data["plan_name"], price)
    await state.clear()
    plans = await rq.get_plans()
    await message.answer("✅ Tarif narxi yangilandi.", reply_markup=main_menu(True))
    await message.answer("💎 Premium tariflari:", reply_markup=admin_premium_kb(plans))


# ---------------------------------------------------------------------------
# PROMO KODLAR
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm:promo")
async def cb_admin_promo(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit(callback, "🎁 <b>Promo kodlar</b> bo'limi:", admin_promo_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "adm_promo:add")
async def cb_add_promo(callback: CallbackQuery, state: FSMContext):
    await rq.ensure_default_plans()
    await state.set_state(AdminPromo.code)
    await callback.message.answer("🎁 Yangi promo kodni kiriting (masalan: KINOPREMIUM7):", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminPromo.code)
async def receive_promo_code_admin(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    if await rq.get_promo_by_code(code):
        await message.answer("❌ Bu kod allaqachon mavjud. Boshqa kod kiriting.")
        return
    await state.update_data(code=code)
    await state.set_state(AdminPromo.choose_plan)
    plans = await rq.get_plans()
    await message.answer("💎 Tarifni tanlang:", reply_markup=plan_choice_kb(plans))


@admin_router.callback_query(F.data.startswith("adm_promo_plan:"), AdminPromo.choose_plan)
async def receive_promo_plan(callback: CallbackQuery, state: FSMContext):
    plan_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    promo = await rq.create_promo(data["code"], plan_id)
    await state.clear()
    plan = await rq.get_plan(plan_id)
    await callback.message.answer(
        f"✅ Promo kod yaratildi!\n\n🎁 Kod: <code>{promo.code}</code>\n"
        f"💎 Tarif: {plan_title(plan.name)} ({plan.duration_days} kun)",
        reply_markup=main_menu(True),
    )
    await callback.message.answer("🎁 Promo kodlar bo'limi:", reply_markup=admin_promo_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "adm_promo:list")
async def cb_list_promo(callback: CallbackQuery):
    promos = await rq.get_all_promos()
    if not promos:
        await callback.answer("❌ Hozircha promo kodlar yo'q.", show_alert=True)
        return
    await safe_edit(callback, "🎁 <b>Promo kodlar</b> ro'yxati:", admin_promo_list_kb(promos))
    await callback.answer()


def _promo_detail_text(promo) -> str:
    status = "✅ Aktiv" if promo.is_active else "🚫 Noaktiv"
    used = f"\n👤 Ishlatgan: <code>{promo.used_by}</code>" if promo.is_used else "\n🆕 Hali ishlatilmagan"
    return (
        f"🎁 Kod: <code>{promo.code}</code>\n"
        f"💎 Tarif: {plan_title(promo.plan.name)} ({promo.plan.duration_days} kun)\n"
        f"📌 Holati: {status}{used}"
    )


@admin_router.callback_query(F.data.startswith("adm_promo:view:"))
async def cb_view_promo(callback: CallbackQuery):
    promo_id = int(callback.data.split(":")[2])
    promo = await rq.get_promo_by_id(promo_id)
    if not promo:
        await callback.answer("❌ Topilmadi", show_alert=True)
        return
    await safe_edit(callback, _promo_detail_text(promo), admin_promo_detail_kb(promo))
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_promo:toggle:"))
async def cb_toggle_promo(callback: CallbackQuery):
    promo_id = int(callback.data.split(":")[2])
    await rq.toggle_promo(promo_id)
    promo = await rq.get_promo_by_id(promo_id)
    await safe_edit(callback, _promo_detail_text(promo), admin_promo_detail_kb(promo))
    await callback.answer("Holat o'zgartirildi")


@admin_router.callback_query(F.data.startswith("adm_promo:delete:"))
async def cb_delete_promo(callback: CallbackQuery):
    promo_id = int(callback.data.split(":")[2])
    await rq.delete_promo(promo_id)
    promos = await rq.get_all_promos()
    if promos:
        await safe_edit(callback, "🗑 Promo kod o'chirildi.\n\n🎁 Promo kodlar ro'yxati:", admin_promo_list_kb(promos))
    else:
        await safe_edit(callback, "🗑 Promo kod o'chirildi.", admin_promo_kb())
    await callback.answer()


# ---------------------------------------------------------------------------
# OMMAVIY XABAR
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm:broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminBroadcast.waiting_content)
    await callback.message.answer(
        "📣 Ommaviy xabar matnini yuboring.\n"
        "Rasm yoki video bilan birga matn yubormoqchi bo'lsangiz, ularni caption sifatida yuboring.",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@admin_router.message(AdminBroadcast.waiting_content)
async def receive_broadcast_content(message: Message, state: FSMContext):
    await state.clear()
    user_ids = await rq.get_all_user_ids()
    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await message.copy_to(chat_id=uid)
            sent += 1
        except Exception:
            failed += 1
    await rq.log_broadcast(sent, failed)
    await message.answer(
        f"📣 Ommaviy xabar yuborildi!\n\n📤 Yuborildi: {sent}\n❌ Yuborilmadi: {failed}",
        reply_markup=main_menu(True),
    )


# ---------------------------------------------------------------------------
# STATISTIKA / SOZLAMALAR
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm:stats")
async def cb_admin_stats(callback: CallbackQuery):
    stats = await rq.get_stats()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
        f"🆕 Bugun qo'shilgan: {stats['today_users']}\n"
        f"💎 Premium: {stats['premium_users']}\n"
        f"🎬 Kinolar: {stats['total_movies']}\n"
        f"📺 Seriallar: {stats['total_series']}"
    )
    await safe_edit(callback, text, back_to_admin_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "adm:settings")
async def cb_admin_settings(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    card1 = await rq.get_setting("card_number_1") or "—"
    card2 = await rq.get_setting("card_number_2") or "—"
    admin_username = await rq.get_setting("admin_username") or "—"
    text = (
        "⚙️ <b>Sozlamalar</b>\n\n"
        f"👤 Adminlar soni: {len(ADMIN_IDS)}\n"
        f"💳 1-karta: <code>{card1}</code>\n"
        f"💳 2-karta: <code>{card2}</code>\n"
        f"👤 Admin username: @{admin_username}\n"
        "🗄 Ma'lumotlar bazasi: SQLite (bot qayta ishga tushganda ham saqlanadi)"
    )
    await safe_edit(callback, text, admin_settings_kb())
    await callback.answer()


# ---------------------------------------------------------------------------
# SOZLAMALAR: PREMIUM
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm_settings:premium")
async def cb_premium_settings(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    template = await rq.get_setting("premium_payment_template") or "—"
    # Faqat birinchi 200 belgisini ko'rsatamiz (preview)
    preview = template[:200] + ("..." if len(template) > 200 else "")
    text = (
        "⚙️ <b>Premium sozlamalari</b>\n\n"
        "📝 Joriy to'lov xabari (preview):\n"
        f"<i>{preview}</i>\n\n"
        "O'zgartirmoqchi bo'lgan parametrni tanlang:"
    )
    await safe_edit(callback, text, admin_premium_settings_kb())
    await callback.answer()


@admin_router.callback_query(F.data == "adm_settings:edit_template")
async def cb_edit_template(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSettings.edit_payment_template)
    hint = (
        "📝 Yangi to'lov xabari matnini yuboring.\n\n"
        "Quyidagi dinamik o'zgaruvchilardan foydalanish mumkin:\n"
        "<code>{tarif}</code> — tanlangan tarif nomi\n"
        "<code>{narx}</code> — narx\n"
        "<code>{card_number_1}</code> — 1-karta raqami\n"
        "<code>{card_number_2}</code> — 2-karta raqami\n"
        "<code>{admin_username}</code> — admin username\n"
        "<code>{user_id}</code> — foydalanuvchi ID\n"
        "<code>{user_name}</code> — foydalanuvchi ismi"
    )
    await callback.message.answer(hint, reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminSettings.edit_payment_template)
async def receive_payment_template(message: Message, state: FSMContext):
    await rq.set_setting("premium_payment_template", message.text)
    await state.clear()
    await message.answer("✅ To'lov xabari shabloni yangilandi.", reply_markup=main_menu(True))


@admin_router.callback_query(F.data == "adm_settings:edit_card1")
async def cb_edit_card1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSettings.edit_card_1)
    await callback.message.answer("💳 Yangi 1-karta raqamini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminSettings.edit_card_1)
async def receive_card1(message: Message, state: FSMContext):
    await rq.set_setting("card_number_1", message.text.strip())
    await state.clear()
    await message.answer(f"✅ 1-karta raqami yangilandi: <code>{message.text.strip()}</code>", reply_markup=main_menu(True))


@admin_router.callback_query(F.data == "adm_settings:edit_card2")
async def cb_edit_card2(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSettings.edit_card_2)
    await callback.message.answer("💳 Yangi 2-karta raqamini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminSettings.edit_card_2)
async def receive_card2(message: Message, state: FSMContext):
    await rq.set_setting("card_number_2", message.text.strip())
    await state.clear()
    await message.answer(f"✅ 2-karta raqami yangilandi: <code>{message.text.strip()}</code>", reply_markup=main_menu(True))


@admin_router.callback_query(F.data == "adm_settings:edit_admin_username")
async def cb_edit_admin_username(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSettings.edit_admin_username)
    await callback.message.answer(
        "👤 Yangi admin username kiriting (@ belgisisiz, masalan: JAMSHID2426):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@admin_router.message(AdminSettings.edit_admin_username)
async def receive_admin_username(message: Message, state: FSMContext):
    username = message.text.strip().lstrip("@")
    await rq.set_setting("admin_username", username)
    await state.clear()
    await message.answer(f"✅ Admin username yangilandi: @{username}", reply_markup=main_menu(True))


# ---------------------------------------------------------------------------
# SERIAL TAHRIRLASH
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm_series:edit")
async def cb_series_edit_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminSeriesEdit.choose_code)
    await callback.message.answer("✏️ Tahrirlash uchun serial kodini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.message(AdminSeriesEdit.choose_code)
async def receive_series_edit_code(message: Message, state: FSMContext):
    series = await rq.get_series_by_code(message.text.strip())
    if not series:
        await message.answer("❌ Bunday kodli serial topilmadi.")
        return
    await state.clear()
    episodes = await rq.get_episodes_by_series(series.id)
    ep_info = f"\n📊 Qismlar soni: {len(episodes)} ta" if episodes else "\n📊 Hali qismlar yo'q"
    await message.answer(
        f"✏️ <b>{series.title}</b> ({series.code}){ep_info}\n\nQaysi maydonni tahrirlaysiz?",
        reply_markup=series_edit_fields_kb(series.id),
    )


@admin_router.callback_query(F.data.startswith("adm_series_edit_f:"))
async def cb_choose_series_edit_field(callback: CallbackQuery, state: FSMContext):
    _, series_id, field = callback.data.split(":")
    series_id = int(series_id)
    if field == "is_premium":
        await state.update_data(series_id=series_id, field=field)
        await state.set_state(AdminSeriesEdit.new_value)
        await callback.message.answer(
            "💎 Serialning yangi maqomini tanlang:",
            reply_markup=premium_choice_kb(prefix="editseriesprem"),
        )
        await callback.answer()
        return
    await state.update_data(series_id=series_id, field=field)
    await state.set_state(AdminSeriesEdit.new_value)
    field_names = {
        "title": "📝 Yangi nomni",
        "description": "📄 Yangi tavsifni",
        "year": "📅 Yangi yilni",
        "quality": "🎞 Yangi sifatni",
        "language": "🗣 Yangi tilni",
        "cover_file_id": "🖼 Yangi cover rasmini",
    }
    prompt = field_names.get(field, "Yangi qiymatni")
    await callback.message.answer(f"{prompt} yuboring:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("editseriesprem:"), AdminSeriesEdit.new_value)
async def receive_edit_series_premium(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_prem = bool(int(callback.data.split(":")[1]))
    await rq.update_series_field(data["series_id"], "is_premium", is_prem)
    await state.clear()
    await callback.message.answer("✅ Serial maqomi yangilandi.", reply_markup=main_menu(True))
    await callback.answer()


@admin_router.message(AdminSeriesEdit.new_value, F.photo)
async def receive_series_edit_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("field") != "cover_file_id":
        await message.answer("❌ Bu maydon uchun rasm emas, matn kerak.")
        return
    await rq.update_series_field(data["series_id"], "cover_file_id", message.photo[-1].file_id)
    await state.clear()
    await message.answer("✅ Cover rasmi yangilandi.", reply_markup=main_menu(True))


@admin_router.message(AdminSeriesEdit.new_value)
async def receive_series_edit_text(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")
    if field == "cover_file_id":
        await message.answer("❌ Iltimos rasm yuboring.")
        return
    await rq.update_series_field(data["series_id"], field, message.text.strip())
    await state.clear()
    await message.answer("✅ Yangilandi.", reply_markup=main_menu(True))


# ---------------------------------------------------------------------------
# QISM (EPISODE) TAHRIRLASH
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data == "adm_series:edit_episode")
async def cb_episode_edit_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminEpisodeEdit.series_code)
    await callback.message.answer("🔢 Qismni tahrirlash uchun serial kodini kiriting:", reply_markup=cancel_kb())
    await callback.answer()


@admin_router.callback_query(F.data.startswith("adm_series_edit_ep:"))
async def cb_edit_episode_from_series(callback: CallbackQuery, state: FSMContext):
    """Serial tahrirlash menyusidan qism tahrirlashga o'tish."""
    series_id = int(callback.data.split(":")[1])
    series = await rq.get_series_by_id(series_id)
    if not series:
        await callback.answer("❌ Serial topilmadi.", show_alert=True)
        return
    await state.update_data(series_id=series_id, series_code=series.code)
    await state.set_state(AdminEpisodeEdit.episode_number)
    episodes = await rq.get_episodes_by_series(series_id)
    ep_list = ", ".join(str(e.episode_number) for e in episodes) if episodes else "hali yo'q"
    await callback.message.answer(
        f"📺 <b>{series.title}</b>\n"
        f"📋 Mavjud qismlar: {ep_list}\n\n"
        "🔢 Tahrirlash uchun qism raqamini kiriting:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@admin_router.message(AdminEpisodeEdit.series_code)
async def receive_episode_edit_series_code(message: Message, state: FSMContext):
    series = await rq.get_series_by_code(message.text.strip())
    if not series:
        await message.answer("❌ Bunday kodli serial topilmadi.")
        return
    await state.update_data(series_id=series.id, series_code=series.code)
    await state.set_state(AdminEpisodeEdit.episode_number)
    episodes = await rq.get_episodes_by_series(series.id)
    ep_list = ", ".join(str(e.episode_number) for e in episodes) if episodes else "hali yo'q"
    await message.answer(
        f"📺 <b>{series.title}</b>\n"
        f"📋 Mavjud qismlar: {ep_list}\n\n"
        "🔢 Tahrirlash uchun qism raqamini kiriting:",
        reply_markup=cancel_kb(),
    )


@admin_router.message(AdminEpisodeEdit.episode_number)
async def receive_episode_edit_number(message: Message, state: FSMContext):
    try:
        ep_num = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Iltimos butun son kiriting.")
        return
    data = await state.get_data()
    series_id = data["series_id"]
    episode = await rq.get_episode_by_series_and_number(series_id, ep_num)
    if not episode:
        await message.answer(f"❌ {ep_num}-qism topilmadi.")
        return
    await state.update_data(episode_id=episode.id, ep_num=ep_num)
    await state.set_state(AdminEpisodeEdit.video)
    await message.answer(
        f"🎬 <b>{ep_num}-qism</b> uchun yangi video faylini yuboring:",
        reply_markup=cancel_kb(),
    )


@admin_router.message(AdminEpisodeEdit.video, F.video)
async def receive_episode_edit_video(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_episode_video(data["episode_id"], message.video.file_id)
    await state.clear()
    await message.answer(
        f"✅ <b>{data['ep_num']}-qism</b> videosi yangilandi.",
        reply_markup=main_menu(True),
    )


@admin_router.message(AdminEpisodeEdit.video)
async def receive_episode_edit_video_invalid(message: Message):
    await message.answer("❌ Iltimos video fayl yuboring.")


# ---------------------------------------------------------------------------
# PREMIUM BUYURTMALARINI TASDIQLASH / RAD ETISH
# ---------------------------------------------------------------------------

@admin_router.callback_query(F.data.startswith("adm_order:confirm:"))
async def cb_confirm_order(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split(":")[2])
    order = await rq.confirm_premium_order(order_id, callback.from_user.id)
    if not order:
        await callback.answer("❌ Buyurtma topilmadi yoki allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    # Premiumni faollashtirish
    plan = await rq.get_plan(order.plan_id)
    if plan:
        until = await rq.activate_premium(order.user_id, plan.duration_days)
        until_str = until.strftime("%d.%m.%Y %H:%M")
    else:
        until_str = "—"

    # Foydalanuvchiga xabar
    try:
        await bot.send_message(
            chat_id=order.user_id,
            text=(
                f"✅ <b>Premium faollashtirildi!</b>\n\n"
                f"💎 Tarif: <b>{plan_title(order.plan_name)} ({plan.duration_days if plan else '?'} kun)</b>\n"
                f"⏳ Muddat: <b>{until_str}</b> gacha\n\n"
                f"Kinochi botidan bahramand bo'ling! 🎬"
            ),
        )
    except Exception:
        pass

    price_str = f"{order.price:,}".replace(",", " ")
    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ <b>Tasdiqlandi!</b> Admin: {callback.from_user.full_name}\nPremium: {until_str} gacha",
        reply_markup=None,
    )
    await callback.answer("✅ Premium faollashtirildi!")


@admin_router.callback_query(F.data.startswith("adm_order:reject:"))
async def cb_reject_order(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.split(":")[2])
    order = await rq.reject_premium_order(order_id, callback.from_user.id)
    if not order:
        await callback.answer("❌ Buyurtma topilmadi yoki allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    # Foydalanuvchiga xabar
    try:
        await bot.send_message(
            chat_id=order.user_id,
            text=(
                "❌ <b>Premium buyurtmangiz rad etildi.</b>\n\n"
                "Agar bu xato deb hisoblasangiz, admin bilan bog'laning."
            ),
        )
    except Exception:
        pass

    await callback.message.edit_text(
        callback.message.text + f"\n\n❌ <b>Rad etildi!</b> Admin: {callback.from_user.full_name}",
        reply_markup=None,
    )
    await callback.answer("❌ Buyurtma rad etildi.")
