from aiogram import Bot
import asyncio

from data.config import TOKEN
from utils.db import get_users_sync
import redis
from celery import Celery
from loguru import logger
from celery.schedules import crontab

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")
app = Celery('tasks', broker='redis://localhost:6379/0')
r = redis.Redis(host="localhost", port=6379)


async def send_message(bot, user_id, text):
    await bot.send_message(chat_id=user_id, text=text)


async def send_messages():
    logger.debug("Starting send_messages task")
    users = get_users_sync()
    logger.debug(f"Users: {users}")
    bot = Bot(token=TOKEN)

    for user in users:
        logger.debug(f"Sending message to {user[0]}")
        try:
            await send_message(bot, user[0], 'Не забудьте проверить уведомления111')
        except Exception as e:
            logger.error(f"Failed to send message to {user[0]}: {e}")
    await bot.session.close()


@app.task
def send_daily_reminder():
    logger.debug("Starting send_daily_reminder task")
    asyncio.run(send_messages())


app.conf.beat_schedule = {
    'send_daily_reminder': {
        'task': 'tasks.send_daily_reminder',
        'schedule': crontab(minute="*/3"),
    },
}

app.conf.update(
    timezone='Asia/Tashkent',
    result_expires=3600
)

app.autodiscover_tasks(['tasks'])