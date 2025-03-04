import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.fsm import LocationState
from use_cases.rating_use_case import rating_use_case

router = Router()


@router.message(Command("rate"))
async def cmd_rate_location(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Понял!\n Отправь мне <b>ссылку на 2ГИС и оценку (до 5)</b> на следующей строке")

    await state.set_state(LocationState.rating_place)


@router.message(LocationState.rating_place, F.text)
async def handle_rate_location(message: Message, state: FSMContext):
    user_id = message.from_user.id
    link, rating = message.text.split('\n')
    rating_data = {
        'user_id': user_id,
        'place_gis_id': re.search(r'\d{6,}', link)[0],
        'rating': rating
    }
    rating = await rating_use_case.create_rating(rating_data=rating_data)

    await message.answer(f"Оценка для заведения <b>{rating['place']['title']}</b> добавлена успешно.")
    await state.clear()
