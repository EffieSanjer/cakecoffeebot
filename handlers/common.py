from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from handlers.location import LocationState

router = Router()


def location_button():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(
            text="Поделиться местоположением \n(Доступно только в приложении)",
            request_location=True
        )
    )
    return builder.as_markup(resize_keyboard=True)


@router.message(StateFilter(None), Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Привет!\n"
                         f"Я бот, который поможет найти, где выпить кофе!")

    await message.answer("Напиши свой город или отправь геолокацию, чтобы я смог найти тебя", reply_markup=location_button())
    await state.set_state(LocationState.choosing_city)


