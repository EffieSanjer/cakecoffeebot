import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram_sqlite_storage.sqlitestore import SQLStorage

from handlers import location, common

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=os.environ['TG_TOKEN'])
    dp = Dispatcher(storage=SQLStorage(os.environ['DB_PATH'], serializing_method='json'))

    dp.include_routers(common.router)
    dp.include_routers(location.router)

    dp["today"] = datetime.now().strftime("%d.%m.%Y")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
