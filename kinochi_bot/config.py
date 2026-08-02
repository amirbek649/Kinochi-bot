import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///kinochi.db")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan!")
if not ADMIN_IDS:
    raise RuntimeError("ADMIN_IDS .env faylida ko'rsatilmagan!")
