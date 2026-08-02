from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from ..config import ADMIN_IDS


class IsAdmin(BaseFilter):
    """Faqat .env dagi ADMIN_IDS ro'yxatidagi foydalanuvchilarga ruxsat beradi."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id in ADMIN_IDS
