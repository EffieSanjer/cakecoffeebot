from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from backend.config import settings
from tg_bot.handlers.location import LocationState
from use_cases.categories_use_case import category_use_case

router = Router()


def location_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Санкт-Петербург"),
        types.KeyboardButton(text="Москва"),
        types.KeyboardButton(
            text="Поделиться местоположением",
            request_location=True
        )
    )
    return builder.as_markup(resize_keyboard=True)


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет!\n Я бот, который поможет найти, где выпить кофе!")

    await message.answer(
        "Напиши свой город или отправь геолокацию, чтобы я смог найти тебя",
        reply_markup=location_kb()
    )
    await state.set_state(LocationState.choosing_city)


@router.message(Command("add"), F.chat.id == settings.ADMIN_TG_ID)
async def cmd_add_location(message: types.Message, state: FSMContext):
    await state.clear()
    categories = await category_use_case.get_categories(by_names=True)

    await message.answer(
        "Понял!\n"
        "Отправь мне <b>ссылку на 2ГИС, название категории и заметку</b> (если есть), каждое на новой строке\n\n"
        f"Список доступных категорий:\n• {categories}"
    )

    await state.set_state(LocationState.creating_place)


@router.message(Command("add"), F.chat.id != settings.ADMIN_TG_ID)
async def cmd_add_location(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Извините, Вам сюда нельзя!")


@router.message(Command("rate"))
async def cmd_rate_location(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer("Понял!\n Отправь мне <b>ссылку на 2ГИС и вашу оценку (до 5)</b> на следующей строке")

    await state.set_state(LocationState.rating_place)


@router.message(Command("clear"))
async def cmd_clear(message: types.Message, state: FSMContext):
    await message.answer(
        "Понял! Я не знаю вас, вы не знаете меня...\n"
        f"(чтобы начать наши отношения снова отправьте /start )",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()


