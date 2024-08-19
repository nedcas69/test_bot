from aiogram.fsm.state import StatesGroup, State


class UserInfo(StatesGroup):
    name = State()
    age = State()
    city = State()


class Echo(StatesGroup):
    text = State()


class Notification(StatesGroup):
    notif = State()
