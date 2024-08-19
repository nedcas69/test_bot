from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from main import bot


async def set_default_commands():
    await bot.set_my_commands([
        BotCommand(command="/start", description="Начать взаимодействие"),
        BotCommand(command="/help", description="Помощь по командам"),
        BotCommand(command="/echo", description="Эхо"),
        BotCommand(command="/stop", description="Остановка Эхо"),
        BotCommand(command="/inline", description="Инлайн кнопки"),
        BotCommand(command="/register", description="Регистрация"),
        BotCommand(command="/weather", description="Информация о погоде"),
        BotCommand(command="/users", description="Информация о пользователях"),
        BotCommand(command="/notification", description="Установить напоминание"),

    ], scope=BotCommandScopeAllPrivateChats())
