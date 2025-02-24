import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_sqlite_storage.sqlitestore import SQLStorage

from backend.config import settings
from tg_bot.handlers import location, common, schedule

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=SQLStorage(settings.DB_PATH, serializing_method='json'))

    dp.include_routers(schedule.router)
    dp.include_routers(common.router)
    dp.include_routers(location.router)

    dp["today"] = datetime.now().strftime("%d.%m.%Y")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
