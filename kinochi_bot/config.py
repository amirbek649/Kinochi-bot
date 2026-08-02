import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///kinochi.db")

# Railway yoki boshqa hostinglar berganda 'postgres://' yoki 'postgresql://' ni SQLAlchemy async drayveriga moslashtirish
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DB_URL.startswith("postgresql://") and not DB_URL.startswith("postgresql+asyncpg://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan!")
if not ADMIN_IDS:
    raise RuntimeError("ADMIN_IDS .env faylida ko'rsatilmagan!")
