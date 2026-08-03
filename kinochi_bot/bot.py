import asyncio
import logging
import sys
import os
from .database.engine import init_db
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from .config import BOT_TOKEN, ADMIN_IDS  # ADMIN_IDS config faylingizda bo'lishi kerak (masalan list yoki bitta id)
from .database.requests import ensure_default_plans
from .handlers.admin_handlers import admin_router
from .handlers.user_handlers import user_router


async def set_bot_commands(bot: Bot):
    # Oddiy foydalanuvchilar uchun komandalar (default scope - hammaga ko'rinadi)
    default_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
    ]
    await bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())

    # Faqat adminlar uchun qo'shimcha /admin komandasi
    admin_commands = default_commands + [
        BotCommand(command="admin", description="Admin panel"),
    ]
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(
                admin_commands,
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except Exception as e:
            logging.warning(f"Admin {admin_id} uchun komandalarni o'rnatib bo'lmadi: {e}")


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    await init_db()
    await ensure_default_plans()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    # admin_router avval ulanadi, chunki u o'z filtrlariga ega (faqat admin uchun ishlaydi)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)
    logging.info("Kinochi bot ishga tushdi.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot to'xtatildi.")
