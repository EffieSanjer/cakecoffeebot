from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from services.geolocation import get_location
from services.place_generation import get_places
from services.weather import get_weather

router = Router()


class LocationState(StatesGroup):
    choosing_city = State()
    choosing_subway = State()


@router.message(LocationState.choosing_city, F.location)
async def handle_geolocation(message: Message, state: FSMContext, today: str):
    lat = message.location.latitude
    lon = message.location.longitude
    weather = get_weather(lat=lat, lon=lon)
    await state.update_data(city=weather['city'])

    await message.answer(f"Твой город {weather['city']}!\n"
                         f"Сегодня {today}, {weather['weather']}, {weather['temp']}℃.\n"
                         f"Отличный день, чтобы прогуляться с кофе!")
    await message.answer("Начнем с простого: в район какого метро Вы хотите отправиться?")
    await state.set_state(LocationState.choosing_subway)


@router.message(LocationState.choosing_city, F.text)
async def handle_text_location(message: Message, state: FSMContext, today: str):
    city = message.text
    await state.update_data(city=city)

    try:
        weather = get_weather(city=city)

        await message.answer(f"Твой город {city}!\n"
                             f"Сегодня {today}, {weather['weather']}, {weather['temp']}℃.\n"
                             f"Отличный день, чтобы прогуляться с кофе!")
    except:
        await message.answer("К сожалению, я не вижу какая сегодня погода, но все равно могу помочь!")

    await message.answer("Начнем с простого: в район какого метро Вы хотите отправиться?")
    await state.set_state(LocationState.choosing_subway)


@router.message(LocationState.choosing_subway, F.text)
async def handle_subway(message: Message, state: FSMContext):
    subway = message.text
    await state.update_data(subway=subway)

    user_data = await state.get_data()
    try:
        result = get_location(city=user_data.get('city'), location=f'станция метро {subway}')

        await message.answer(
            text=f"Отлично!\n{result['name']}\nИщу заведения в 10-15 минутах ходьбы...",
        )
        places = get_places(result['geometry']['lat'], result['geometry']['lng'], 15)
        nl = '\n'.join(map(str, places))
        await message.answer(
            text=f"Вот список ближайших мест:\n{nl}",
        )
    except:
        await message.answer(
            text=f"Кажется, сегодня не работаю(\nЗагляните в другой день",
        )

    await state.clear()


@router.message()
async def handle_subway_incorrectly(message: Message):
    await message.answer(
        text="Я Вас не понял, давайте попробуем еще раз.\n"
             "Пожалуйста, напишите еще раз."
    )
