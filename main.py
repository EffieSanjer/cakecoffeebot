import asyncio
from datetime import datetime

from aiogram.types import BotCommand, BotCommandScopeDefault

from bot import bot, admins, dp
from tg_bot.handlers import start_router, get_locations_router, add_location_router, rate_location_router


async def set_commands():
    commands = [
        BotCommand(command='start', description='Старт'),
        BotCommand(command='add', description='Добавить заведение'),
        BotCommand(command='rate', description='Оценить заведение'),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    # await set_commands()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass


async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except:
        pass


async def main():
    dp.include_routers(start_router.start_router)
    dp.include_routers(get_locations_router.router)
    dp.include_routers(add_location_router.router)
    dp.include_routers(rate_location_router.router)

    # dp.startup.register(start_bot)
    # dp.shutdown.register(stop_bot)

    dp["today"] = datetime.now().strftime("%d.%m.%Y")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

