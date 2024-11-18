import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_sqlite_storage.sqlitestore import SQLStorage
from decouple import config

from handlers import location, common

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=config('TG_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=SQLStorage(config('DB_PATH'), serializing_method='json'))

    dp.include_routers(common.router)
    dp.include_routers(location.router)

    dp["today"] = datetime.now().strftime("%d.%m.%Y")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

