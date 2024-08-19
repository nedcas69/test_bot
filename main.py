import asyncio

from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from handlers.handlers import get_router
from utils.db import init_db
from data.config import TOKEN

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")
bot = Bot(token=TOKEN)
storage = RedisStorage.from_url('redis://localhost:6379/1')
dp = Dispatcher(storage=storage)


async def main():
    logger.debug("Главная функция:")
    await init_db()
    router = get_router()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
