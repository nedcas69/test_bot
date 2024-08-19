import asyncio
import requests
import aioredis

from PIL import Image
from aiogram import types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from utils.fsm import UserInfo, Echo, Notification
from utils.db import save_user_to_db, get_users
from data.config import API_KEY, TOKEN

API_KEY = API_KEY
bot = Bot(token=TOKEN)
router = Router()
redis = aioredis.from_url("redis://localhost:6379/1")


async def remind_user(user_id: int, chat_id: int):
    try:
        await asyncio.sleep(15)
        if await redis.get(f'timer:{user_id}') == b'active':
            await bot.send_message(chat_id, 'Вы забыли ответить')
    except asyncio.CancelledError:
        pass
    finally:
        await redis.delete(f'task:{user_id}')
        await redis.delete(f'timer:{user_id}')


@router.message(Command(commands=["notification"]))
async def notification(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id

    await message.answer(
        "Напоминание на 15 минут")
    await message.answer(f"Привет, {message.from_user.full_name}! Как ты сегодня?")

    await redis.set(f'timer:{user_id}', 'active')

    existing_task_id = await redis.get(f'task:{user_id}')
    if existing_task_id:
        await redis.delete(f'timer:{user_id}')

    task = asyncio.create_task(remind_user(user_id, chat_id))

    await redis.set(f'task:{user_id}', str(task.get_name()))
    print(await redis.get(f'timer:{user_id}'))
    await state.set_state(Notification.notif)


@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message):
    await message.answer("Добро пожаловать в наш бот!")


@router.message(Command(commands=["help"]))
async def send_help(message: types.Message):
    await message.answer("Доступные команды: \n/start \n/help \n/echo \n/stop \n/register \n/inline "
                         "\n/weather \n/users \n/notification ")


@router.message(Command(commands=["echo"]))
async def echo(message: types.Message, state: FSMContext):

    await message.answer("Напишите для Эхо! Для остановки эхо нажмите на команду /stop")
    await state.set_state(Echo.text)


@router.message(Command(commands=["stop"]))
async def stop(message: types.Message, state: FSMContext):
    await message.answer(text="Эхо остановлено.")
    await state.clear()


@router.message(Echo.text)
async def echo_state(message: types.Message, state: FSMContext):
    await message.answer(text=message.text)
    await state.set_state(Echo.text)


@router.message(Command(commands=["inline"]))
async def inline_buttons(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбор 1", callback_data='choice1')],
        [InlineKeyboardButton(text="Выбор 2", callback_data='choice2')]
    ])
    await message.answer("Выберите опцию:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data in ['choice1', 'choice2'])
async def handle_callback(callback_query: types.CallbackQuery):
    if callback_query.data == 'choice1':
        await callback_query.message.answer("Вы выбрали Выбор 1")
    elif callback_query.data == 'choice2':
        await callback_query.message.answer("Вы выбрали Выбор 2")
    await callback_query.answer()


@router.message(lambda message: message.photo)
async def handle_photo(message: types.Message):
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file = await message.bot.download_file(file_info.file_path)
    with Image.open(file) as img:
        width, height = img.size
    await message.answer(f"Размер изображения: {width}x{height} пикселей")


@router.message(Command(commands=["register"]))
async def register(message: types.Message, state: FSMContext):
    await message.answer("Как тебя зовут?")
    await state.set_state(UserInfo.name)


@router.message(UserInfo.name)
async def process_name(message: types.Message, state: FSMContext):
    try:
        name = message.text

        def contains_digits(s):
            return any(char.isdigit() for char in s)

        if not contains_digits(name) and len(name) >= 2:
            await state.update_data(name=name)
            await message.answer("Сколько тебе лет?")
            await state.set_state(UserInfo.age)
        else:
            await message.answer("Ошибка! Имя должно быть написано буквами и состоять минимум из двух букв!")
    except:
        await message.answer("Ошибка! Имя должно быть написано буквами и состоять минимум из двух букв!")


@router.message(UserInfo.age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        data = await state.get_data()
        await message.answer(f"Привет, {data['name']}! Тебе {data['age']} лет.")
        await save_user_to_db(message.from_user.id, data['name'], data['age'])
        await state.clear()
    except:
        await message.answer("<b>Ошибка!!! Возраст нужно писать цифрами!</b>")


@router.message(Command(commands=["weather"]))
async def weather(message: types.Message, state: FSMContext):
    await message.answer("Введите название города:")
    await state.set_state(UserInfo.city)


@router.message(UserInfo.city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru'
    response = requests.get(url).json()
    if response.get('cod') == 200:
        weather_description = response['weather'][0]['description']
        temperature = response['main']['temp']
        await message.answer(f"Погода в {city}: {weather_description}, температура: {temperature}°C")
    else:
        await message.answer("Не удалось получить данные о погоде. Попробуйте позже.")
    await state.clear()


@router.message(Command(commands=["users"]))
async def list_users(message: types.Message):
    users = await get_users()
    if users:
        response = "\n".join([f"ID: {user[0]}, Имя: {user[1]}, Возраст: {user[2]}" for user in users])

        await message.answer(response)
    else:
        await message.answer("Нет пользователей в базе данных.")


@router.message(Notification.notif)
async def notification_state(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await redis.delete(f'timer:{user_id}')

    existing_task_id = await redis.get(f'task:{user_id}')
    if existing_task_id:
        task = asyncio.tasks.current_task(existing_task_id.decode())
        if task:
            task.cancel()

        await redis.delete(f'task:{user_id}')
    await state.clear()
    await message.answer("Напоминание удалено.")


def get_router() -> Router:
    return router
