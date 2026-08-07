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
from .database import requests as rq
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


async def cleanup_expired_premiums_loop(bot: Bot):
    logging.info("Premium obunalarni va xabarlarni tozalash vazifasi boshlandi.")
    while True:
        try:
            # 1. Muddati tugagan premiumlarni faolsizlantirish
            await rq.deactivate_expired_premiums()
            
            # 2. Premium bo'lmagan foydalanuvchilarning premium xabarlarini tozalash
            expired_logs = await rq.get_expired_premium_message_logs()
            
            for user_id, msg_ids in expired_logs.items():
                deleted_msg_ids = []
                for msg_id in msg_ids:
                    try:
                        await bot.delete_message(chat_id=user_id, message_id=msg_id)
                        logging.info(f"O'chirildi: premium xabar {msg_id}, chat {user_id}")
                    except Exception as e:
                        # Xabar allaqachon o'chirilgan bo'lishi yoki foydalanuvchi botni bloklagan bo'lishi mumkin
                        logging.debug(f"Xabarni o'chirib bo'lmadi {msg_id} (chat: {user_id}): {e}")
                    deleted_msg_ids.append(msg_id)
                if deleted_msg_ids:
                    await rq.delete_premium_message_logs(user_id, deleted_msg_ids)
        except Exception as e:
            logging.error(f"cleanup_expired_premiums_loop da xatolik: {e}")
        
        await asyncio.sleep(60)



async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    await init_db()
    await rq.ensure_default_plans()
    await rq.ensure_default_settings()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    # admin_router avval ulanadi, chunki u o'z filtrlariga ega (faqat admin uchun ishlaydi)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)
    
    # Premium obunalar tugaganda videolarni o'chirish loopini ishga tushiramiz
    asyncio.create_task(cleanup_expired_premiums_loop(bot))
    
    logging.info("Kinochi bot ishga tushdi.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot to'xtatildi.")
