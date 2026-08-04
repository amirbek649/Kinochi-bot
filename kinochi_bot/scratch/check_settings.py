import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

# We can override DATABASE_URL using DB_URL from dotenv if DATABASE_URL is not set
if not os.getenv("DATABASE_URL") and os.getenv("DB_URL"):
    os.environ["DATABASE_URL"] = os.getenv("DB_URL")

from ..database.engine import init_db, async_session
from ..database.models import BotSettings
from ..database.requests import get_setting, ensure_default_settings
from ..sqlalchemy import select

async def main():
    await init_db()
    await ensure_default_settings()
    
    async with async_session() as session:
        result = await session.execute(select(BotSettings))
        settings = result.scalars().all()
        print("--- Jadvaldagi sozlamalar ---")
        for s in settings:
            print(f"{s.key}: {s.value}")
        
    val1 = await get_setting("premium_payment_template")
    val2 = await get_setting("card_number_1")
    val3 = await get_setting("card_number_2")
    val4 = await get_setting("admin_username")
    
    print("\n--- get_setting natijalari ---")
    print(f"template: {val1}")
    print(f"card1: {val2}")
    print(f"card2: {val3}")
    print(f"admin_username: {val4}")

if __name__ == "__main__":
    asyncio.run(main())

