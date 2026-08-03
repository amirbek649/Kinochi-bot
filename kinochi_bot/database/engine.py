import os 
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from ..config import DB_URL
from .models import Base

# Railway avtomatik DATABASE_URL yaratadi
DB_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")

# Agar URL "postgresql://" bilan boshlansa, uni async versiyaga o'zgartirish
if DB_URL.startswith("postgresql://") and "+asyncpg" not in DB_URL:
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DB_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    """Bazani va barcha jadvallarni yaratadi hamda yangi ustunlarni tekshiradi."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Jadvallarga yangi ustunlarni xavfsiz qo'shish (SQLite va Postgres mosligi)
        for table, col, col_type in [
            ("movies", "is_premium", "BOOLEAN DEFAULT FALSE"),
            ("series", "is_premium", "BOOLEAN DEFAULT FALSE"),
            ("premium_plans", "price", "BIGINT DEFAULT 0"),
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
            except Exception:
                pass  # Ustun allaqachon mavjud bo'lsa

