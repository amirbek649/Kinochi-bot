from datetime import datetime, timedelta

from sqlalchemy import select, func, delete as sa_delete

from .engine import async_session
from .models import (
    User, Category, Movie, Series, Episode,
    RequiredChannel, PremiumPlan, PromoCode, BroadcastLog,
    PremiumOrder, BotSettings,
)


# ---------------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------------

async def get_or_create_user(tg_user) -> User:
    async with async_session() as session:
        user = await session.get(User, tg_user.id)
        if user is None:
            user = User(
                id=tg_user.id,
                username=tg_user.username,
                full_name=tg_user.full_name,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            # yangilanishlarni saqlab qo'yamiz (username o'zgargan bo'lishi mumkin)
            user.username = tg_user.username
            user.full_name = tg_user.full_name
            await session.commit()
        return user


async def get_user(user_id: int) -> User | None:
    async with async_session() as session:
        return await session.get(User, user_id)


async def refresh_premium_status(user_id: int) -> bool:
    """Muddati tugagan premium foydalanuvchini avtomatik oddiy holatga qaytaradi.
    Qaytaradi: hozirda premiummi (True/False)."""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            return False
        if user.is_premium and user.premium_until and user.premium_until < datetime.utcnow():
            user.is_premium = False
            user.premium_until = None
            await session.commit()
        return user.is_premium


async def activate_premium(user_id: int, days: int) -> datetime:
    async with async_session() as session:
        user = await session.get(User, user_id)
        now = datetime.utcnow()
        base = user.premium_until if (user.premium_until and user.premium_until > now) else now
        new_until = base + timedelta(days=days)
        user.is_premium = True
        user.premium_until = new_until
        await session.commit()
        return new_until


async def get_all_user_ids() -> list[int]:
    async with async_session() as session:
        result = await session.execute(select(User.id).where(User.is_banned == False))  # noqa: E712
        return [row[0] for row in result.all()]


# ---------------------------------------------------------------------------
# CATEGORIES
# ---------------------------------------------------------------------------

async def add_category(name: str) -> Category:
    async with async_session() as session:
        cat = Category(name=name)
        session.add(cat)
        await session.commit()
        await session.refresh(cat)
        return cat


async def get_categories() -> list[Category]:
    async with async_session() as session:
        result = await session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())


async def get_category(category_id: int) -> Category | None:
    async with async_session() as session:
        return await session.get(Category, category_id)


async def delete_category(category_id: int) -> None:
    async with async_session() as session:
        cat = await session.get(Category, category_id)
        if cat:
            await session.delete(cat)
            await session.commit()


# ---------------------------------------------------------------------------
# MOVIES
# ---------------------------------------------------------------------------

async def add_movie(**kwargs) -> Movie:
    async with async_session() as session:
        movie = Movie(**kwargs)
        session.add(movie)
        await session.commit()
        await session.refresh(movie)
        return movie


async def get_movie_by_code(code: str) -> Movie | None:
    async with async_session() as session:
        result = await session.execute(select(Movie).where(Movie.code == code))
        return result.scalar_one_or_none()


async def get_movie_by_id(movie_id: int) -> Movie | None:
    async with async_session() as session:
        return await session.get(Movie, movie_id)


async def search_movies_by_title(query: str, limit: int = 15) -> list[Movie]:
    async with async_session() as session:
        result = await session.execute(
            select(Movie).where(Movie.title.ilike(f"%{query}%")).limit(limit)
        )
        return list(result.scalars().all())


async def get_movies_by_category(category_id: int) -> list[Movie]:
    async with async_session() as session:
        result = await session.execute(select(Movie).where(Movie.category_id == category_id))
        return list(result.scalars().all())


async def update_movie_field(movie_id: int, field: str, value) -> None:
    async with async_session() as session:
        movie = await session.get(Movie, movie_id)
        if movie:
            setattr(movie, field, value)
            await session.commit()


async def delete_movie(movie_id: int) -> None:
    async with async_session() as session:
        movie = await session.get(Movie, movie_id)
        if movie:
            await session.delete(movie)
            await session.commit()


async def count_movies() -> int:
    async with async_session() as session:
        result = await session.execute(select(func.count(Movie.id)))
        return result.scalar_one()


# ---------------------------------------------------------------------------
# SERIES / EPISODES
# ---------------------------------------------------------------------------

async def add_series(**kwargs) -> Series:
    async with async_session() as session:
        series = Series(**kwargs)
        session.add(series)
        await session.commit()
        await session.refresh(series)
        return series


async def get_series_by_code(code: str) -> Series | None:
    async with async_session() as session:
        result = await session.execute(select(Series).where(Series.code == code))
        return result.scalar_one_or_none()


async def get_series_by_id(series_id: int) -> Series | None:
    async with async_session() as session:
        return await session.get(Series, series_id)


async def get_all_series() -> list[Series]:
    async with async_session() as session:
        result = await session.execute(select(Series).order_by(Series.title))
        return list(result.scalars().all())


async def delete_series(series_id: int) -> None:
    async with async_session() as session:
        series = await session.get(Series, series_id)
        if series:
            await session.execute(sa_delete(Episode).where(Episode.series_id == series_id))
            await session.delete(series)
            await session.commit()


async def add_episode(series_id: int, episode_number: int, video_file_id: str) -> Episode:
    async with async_session() as session:
        ep = Episode(series_id=series_id, episode_number=episode_number, video_file_id=video_file_id)
        session.add(ep)
        await session.commit()
        await session.refresh(ep)
        return ep


async def get_episodes_by_series(series_id: int) -> list[Episode]:
    async with async_session() as session:
        result = await session.execute(
            select(Episode).where(Episode.series_id == series_id).order_by(Episode.episode_number)
        )
        return list(result.scalars().all())


async def get_episode_by_id(episode_id: int) -> Episode | None:
    async with async_session() as session:
        return await session.get(Episode, episode_id)


async def count_series() -> int:
    async with async_session() as session:
        result = await session.execute(select(func.count(Series.id)))
        return result.scalar_one()


# ---------------------------------------------------------------------------
# REQUIRED CHANNELS
# ---------------------------------------------------------------------------

async def add_channel(title: str, username: str) -> RequiredChannel:
    async with async_session() as session:
        ch = RequiredChannel(title=title, username=username)
        session.add(ch)
        await session.commit()
        await session.refresh(ch)
        return ch


async def get_channels() -> list[RequiredChannel]:
    async with async_session() as session:
        result = await session.execute(select(RequiredChannel))
        return list(result.scalars().all())


async def delete_channel(channel_id: int) -> None:
    async with async_session() as session:
        ch = await session.get(RequiredChannel, channel_id)
        if ch:
            await session.delete(ch)
            await session.commit()


# ---------------------------------------------------------------------------
# PREMIUM PLANS
# ---------------------------------------------------------------------------

DEFAULT_PLANS = [
    ("daily", 1, 5000),
    ("weekly", 7, 25000),
    ("monthly", 30, 70000),
]


async def ensure_default_plans() -> None:
    async with async_session() as session:
        for name, days, price in DEFAULT_PLANS:
            result = await session.execute(select(PremiumPlan).where(PremiumPlan.name == name))
            plan = result.scalar_one_or_none()
            if plan is None:
                session.add(PremiumPlan(name=name, duration_days=days, price=price))
            else:
                if not plan.price:
                    plan.price = price
        await session.commit()


async def get_plans() -> list[PremiumPlan]:
    async with async_session() as session:
        result = await session.execute(select(PremiumPlan))
        return list(result.scalars().all())


async def get_plan(plan_id: int) -> PremiumPlan | None:
    async with async_session() as session:
        return await session.get(PremiumPlan, plan_id)


async def get_plan_by_name(name: str) -> PremiumPlan | None:
    async with async_session() as session:
        result = await session.execute(select(PremiumPlan).where(PremiumPlan.name == name))
        return result.scalar_one_or_none()


async def set_plan_duration(name: str, days: int) -> None:
    async with async_session() as session:
        result = await session.execute(select(PremiumPlan).where(PremiumPlan.name == name))
        plan = result.scalar_one_or_none()
        if plan:
            plan.duration_days = days
        else:
            session.add(PremiumPlan(name=name, duration_days=days, price=0))
        await session.commit()


async def set_plan_price(name: str, price: int) -> None:
    async with async_session() as session:
        result = await session.execute(select(PremiumPlan).where(PremiumPlan.name == name))
        plan = result.scalar_one_or_none()
        if plan:
            plan.price = price
        else:
            session.add(PremiumPlan(name=name, duration_days=1, price=price))
        await session.commit()



# ---------------------------------------------------------------------------
# PROMO CODES
# ---------------------------------------------------------------------------

async def create_promo(code: str, plan_id: int) -> PromoCode:
    async with async_session() as session:
        promo = PromoCode(code=code, plan_id=plan_id)
        session.add(promo)
        await session.commit()
        await session.refresh(promo)
        return promo


async def get_promo_by_code(code: str) -> PromoCode | None:
    async with async_session() as session:
        result = await session.execute(select(PromoCode).where(PromoCode.code == code))
        return result.scalar_one_or_none()


async def get_promo_by_id(promo_id: int) -> PromoCode | None:
    async with async_session() as session:
        return await session.get(PromoCode, promo_id)


async def get_all_promos() -> list[PromoCode]:
    async with async_session() as session:
        result = await session.execute(select(PromoCode).order_by(PromoCode.created_at.desc()))
        return list(result.scalars().all())


async def toggle_promo(promo_id: int) -> None:
    async with async_session() as session:
        promo = await session.get(PromoCode, promo_id)
        if promo:
            promo.is_active = not promo.is_active
            await session.commit()


async def delete_promo(promo_id: int) -> None:
    async with async_session() as session:
        promo = await session.get(PromoCode, promo_id)
        if promo:
            await session.delete(promo)
            await session.commit()


async def use_promo(code: str, user_id: int) -> tuple[bool, str, int | None]:
    """Promo kodni ishlatishga urinadi.
    Qaytaradi: (muvaffaqiyatmi, xabar, berilgan_kunlar_soni)"""
    async with async_session() as session:
        result = await session.execute(select(PromoCode).where(PromoCode.code == code))
        promo = result.scalar_one_or_none()
        if promo is None:
            return False, "❌ Bunday promo kod topilmadi.", None
        if not promo.is_active:
            return False, "❌ Bu promo kod faol emas.", None
        if promo.is_used:
            return False, "❌ Bu promo kod allaqachon ishlatilgan.", None

        plan = await session.get(PremiumPlan, promo.plan_id)
        if plan is None:
            return False, "❌ Bu promo kodga tegishli tarif topilmadi.", None

        promo.is_used = True
        promo.used_by = user_id
        promo.used_at = datetime.utcnow()
        await session.commit()
        return True, "✅ Promo kod muvaffaqiyatli aktivlashtirildi!", plan.duration_days


# ---------------------------------------------------------------------------
# STATISTICS
# ---------------------------------------------------------------------------

async def get_stats() -> dict:
    async with async_session() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar_one()

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_users = (
            await session.execute(select(func.count(User.id)).where(User.joined_at >= today_start))
        ).scalar_one()

        premium_users = (
            await session.execute(select(func.count(User.id)).where(User.is_premium == True))  # noqa: E712
        ).scalar_one()

        total_movies = (await session.execute(select(func.count(Movie.id)))).scalar_one()
        total_series = (await session.execute(select(func.count(Series.id)))).scalar_one()

        return {
            "total_users": total_users,
            "today_users": today_users,
            "premium_users": premium_users,
            "total_movies": total_movies,
            "total_series": total_series,
        }


async def log_broadcast(sent: int, failed: int) -> None:
    async with async_session() as session:
        session.add(BroadcastLog(sent_count=sent, failed_count=failed))
        await session.commit()


# ---------------------------------------------------------------------------
# SERIES TAHRIRLASH
# ---------------------------------------------------------------------------

async def update_series_field(series_id: int, field: str, value) -> None:
    async with async_session() as session:
        series = await session.get(Series, series_id)
        if series:
            setattr(series, field, value)
            await session.commit()


async def get_episode_by_series_and_number(series_id: int, episode_number: int) -> "Episode | None":
    async with async_session() as session:
        result = await session.execute(
            select(Episode).where(
                Episode.series_id == series_id,
                Episode.episode_number == episode_number,
            )
        )
        return result.scalar_one_or_none()


async def update_episode_video(episode_id: int, video_file_id: str) -> None:
    async with async_session() as session:
        ep = await session.get(Episode, episode_id)
        if ep:
            ep.video_file_id = video_file_id
            await session.commit()


async def delete_episode(episode_id: int) -> None:
    async with async_session() as session:
        ep = await session.get(Episode, episode_id)
        if ep:
            await session.delete(ep)
            await session.commit()


# ---------------------------------------------------------------------------
# PREMIUM ORDERS (buyurtmalar)
# ---------------------------------------------------------------------------

async def create_premium_order(
    user_id: int,
    username: str | None,
    full_name: str | None,
    plan_id: int,
    plan_name: str,
    price: int,
) -> PremiumOrder:
    async with async_session() as session:
        order = PremiumOrder(
            user_id=user_id,
            username=username,
            full_name=full_name,
            plan_id=plan_id,
            plan_name=plan_name,
            price=price,
            status="pending",
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order


async def get_premium_order(order_id: int) -> PremiumOrder | None:
    async with async_session() as session:
        return await session.get(PremiumOrder, order_id)


async def confirm_premium_order(order_id: int, admin_id: int) -> PremiumOrder | None:
    async with async_session() as session:
        order = await session.get(PremiumOrder, order_id)
        if order and order.status == "pending":
            order.status = "paid"
            order.confirmed_at = datetime.utcnow()
            order.confirmed_by = admin_id
            await session.commit()
            await session.refresh(order)
        return order


async def reject_premium_order(order_id: int, admin_id: int) -> PremiumOrder | None:
    async with async_session() as session:
        order = await session.get(PremiumOrder, order_id)
        if order and order.status == "pending":
            order.status = "rejected"
            order.confirmed_at = datetime.utcnow()
            order.confirmed_by = admin_id
            await session.commit()
            await session.refresh(order)
        return order


# ---------------------------------------------------------------------------
# BOT SETTINGS (key-value sozlamalar)
# ---------------------------------------------------------------------------

DEFAULT_PAYMENT_TEMPLATE = (
    "💎 <b>Premium xarid qilish</b>\n\n"
    "Siz tanlagan tarif: <b>{tarif}</b>\n"
    "💰 To'lov summasi: <b>{narx} so'm</b>\n\n"
    "Quyidagi karta raqamlaridan biriga to'lovni amalga oshiring:\n\n"
    "💳 <code>{card_number_1}</code>\n"
    "💳 <code>{card_number_2}</code>\n\n"
    "To'lovni amalga oshirgandan so'ng, to'lov chekini:\n\n"
    "👉 @{admin_username}\n\n"
    "adminiga yuboring.\n\n"
    "⚠️ Chekni yuborishda Telegram profilingizdan yuboring, shunda to'lovni aniqlash oson bo'ladi.\n\n"
    "✅ Admin to'lovni tekshirgandan so'ng Premium hisobingiz faollashtiriladi."
)

DEFAULT_SETTINGS = {
    "premium_payment_template": DEFAULT_PAYMENT_TEMPLATE,
    "card_number_1": "9860606752256077",
    "card_number_2": "9860606752256077",
    "admin_username": "JAMSHID2426",
}


async def ensure_default_settings() -> None:
    """Default sozlamalarni yaratadi (agar mavjud bo'lmasa)."""
    async with async_session() as session:
        for key, value in DEFAULT_SETTINGS.items():
            existing = await session.get(BotSettings, key)
            if existing is None:
                session.add(BotSettings(key=key, value=value))
        await session.commit()


async def get_setting(key: str) -> str | None:
    async with async_session() as session:
        setting = await session.get(BotSettings, key)
        return setting.value if setting else DEFAULT_SETTINGS.get(key)


async def set_setting(key: str, value: str) -> None:
    async with async_session() as session:
        setting = await session.get(BotSettings, key)
        if setting:
            setting.value = value
        else:
            session.add(BotSettings(key=key, value=value))
        await session.commit()
