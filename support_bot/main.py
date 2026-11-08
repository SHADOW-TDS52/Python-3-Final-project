import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, DB_NAME
from database import init_db
from handlers import handle_message, handle_callback

logging.basicConfig(level=logging.INFO)

async def main():
    init_db(DB_NAME)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.message.register(handle_message)
    dp.callback_query.register(handle_callback)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
