import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
import user_handler
import admin_handler

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(admin_handler.router)
    dp.include_router(user_handler.router)
    
    print("✅ MGAS Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
