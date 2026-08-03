import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from .models import Base

# 🔴 MUHIM: Railway DATABASE_URL dan foydalaning (DB_URL emas)
DB_URL = os.getenv("DATABASE_URL")  # Railway avtomatik yaratadi

# Agar DATABASE_URL bo'lmasa, xatolik chiqaramiz
if not DB_URL:
    print("❌ DATABASE_URL environment variable is not set!")
    print("⚠️  Using default local database URL for development")
    DB_URL = "postgresql+asyncpg://postgres:password@localhost:5432/railway"

# Railway URL ni to'g'rilash - "postgresql://" ni "postgresql+asyncpg://" ga o'zgartirish
if DB_URL.startswith("postgresql://") and "+asyncpg" not in DB_URL:
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"✅ Database URL configured: {DB_URL[:40]}...")  # Debug uchun

# Engine yaratish
engine = create_async_engine(DB_URL, echo=False)

# Async session yaratish
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    """Bazani va barcha jadvallarni yaratadi hamda yangi ustunlarni tekshiradi."""
    try:
        async with engine.begin() as conn:
            # Jadvallarni yaratish
            await conn.run_sync(Base.metadata.create_all)
            
            # Jadvallarga yangi ustunlarni xavfsiz qo'shish
            for table, col, col_type in [
                ("movies", "is_premium", "BOOLEAN DEFAULT FALSE"),
                ("series", "is_premium", "BOOLEAN DEFAULT FALSE"),
                ("premium_plans", "price", "BIGINT DEFAULT 0"),
            ]:
                try:
                    # PostgreSQL uchun ustun mavjudligini tekshirish
                    check_query = text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='{table}' AND column_name='{col}'
                    """)
                    result = await conn.execute(check_query)
                    exists = result.fetchone()
                    
                    if not exists:
                        await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                        print(f"✅ Added column {col} to {table}")
                except Exception as e:
                    print(f"⚠️  Could not add column {col} to {table}: {e}")
            
            print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

async def get_db():
    """Database session generator"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
