from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import logger
from config import settings
from core.categories_use_case import category_use_case
from db.exceptions import PlaceAlreadyExistsException
from services.geolocation import add_new_location
from tg_bot.fsm import LocationState

router = Router()


@router.message(Command("add"), F.chat.id == settings.ADMINS_TG_ID[0])
async def cmd_add_location(message: Message, state: FSMContext):
    categories = await category_use_case.get_categories(by_names=True)

    await message.answer(
        "Понял!\n"
        "Отправь мне <b>ссылку на 2ГИС, название категории и заметку</b> (если есть), каждое на новой строке\n\n"
        f"Список доступных категорий:\n• {categories}"
    )

    await state.set_state(LocationState.creating_place)


@router.message(Command("add"), F.chat.id != settings.ADMINS_TG_ID[0])
async def cmd_add_location(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Извините, Вам сюда нельзя!")


@router.message(LocationState.creating_place, F.text)
async def creating_place(message: Message, state: FSMContext):
    msg = message.text

    try:
        new_place = await add_new_location(*msg.split('\n'))
        await message.answer(f"<b>{new_place['title']}</b> успешно добавлено на карту!")

    except PlaceAlreadyExistsException as e:
        logger.error(f'PlaceExists error: {e}')
        await message.answer(f"Заведение уже добавлено на карту!")

    except Exception as e:
        logger.error(f'Unknown error: {e}')
        await message.answer(f"Что-то пошло не так, попробуйте еще раз!")

    finally:
        await state.clear()

