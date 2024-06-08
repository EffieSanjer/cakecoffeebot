import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from services.weather import get_weather

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ['TG_TOKEN'])
dp = Dispatcher()

# dispatcher settings
dp["today"] = datetime.now().strftime("%d.%m.%Y")


@dp.message(Command("start"))
async def cmd_start(message: types.Message, today: str):
    weather = get_weather('Москва')
    await message.answer("Привет!\n"
                         f"Сегодня {today}, {weather['weather']}, {weather['temp']}C.\n"
                         f"Отличный день, чтобы прогуляться с кофе!")
    await message.answer("Начнем с простого: в район какого метро Вы хотите отправиться?")


async def main():
    await dp.start_polling(bot)
