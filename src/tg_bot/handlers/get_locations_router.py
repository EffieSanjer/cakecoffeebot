import httpx
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from src.bot import logger
from src.services.geolocation import get_location
from src.services.weather import get_weather
from src.tg_bot.fsm import LocationState
from src.tg_bot.keyboards.place_kbs import NumbersCallbackFactory, generate_places_kb
from src.tg_bot.utils import send_places_on_map, callback_str_place_info

router = Router()


@router.message(LocationState.choosing_city, F.location)
async def handle_geolocation(message: Message, state: FSMContext, today: str):
    lat = message.location.latitude
    lon = message.location.longitude

    try:
        weather = await get_weather(lat=lat, lon=lon)
        await state.update_data(city=weather['city'])

        location = await get_location(city=weather['city'], lat=lat, lon=lon)
        await state.update_data(address={'lat': lat, 'lon': lon})

        await state.set_state(LocationState.choosing_address)

        await message.answer(
            f"Твой адрес: {location['name']}!\n "
            f"Сегодня {today}, {weather['weather']}, {weather['temp']}℃.\n\n"
            f"Ищу заведения в 10-15 минутах ходьбы...",
            reply_markup=ReplyKeyboardRemove()
        )
    except httpx.HTTPStatusError as e:
        logger.error(f'API error: {e}')
        await message.answer(f"Кажется, сегодня не работаю(\nЗагляните в другой день")
        return

    await send_places_on_map(message, lat, lon, state)


@router.message(LocationState.choosing_city, F.text)
async def handle_text_location(message: Message, state: FSMContext, today: str):
    city = message.text
    await state.update_data(city=city)

    try:
        weather = await get_weather(city=city)

        await message.answer(
            f"Твой город: {city}!\n"
            f"Сегодня {today}, {weather['weather']}, {weather['temp']}℃.\n"
            f"Отличный день, чтобы прогуляться с кофе!",
            reply_markup=ReplyKeyboardRemove()
        )
    except httpx.HTTPStatusError as e:
        logger.error(f'API error: {e}')
        await message.answer(
            "К сожалению, я не вижу какая сегодня погода, но все равно могу помочь!",
            reply_markup=ReplyKeyboardRemove()
        )

    await message.answer("Начнем с простого: в район какого метро Вы хотите отправиться?")
    await state.set_state(LocationState.choosing_address)


@router.message(LocationState.choosing_address, F.text)
async def handle_subway(message: Message, state: FSMContext):
    subway = message.text
    await state.update_data(address=subway)

    user_data = await state.get_data()
    try:
        result = await get_location(city=user_data.get('city'), location=f'станция метро {subway}')
        lat, lon = result['geometry']['lat'], result['geometry']['lng']
        await state.update_data(address={'lat': lat, 'lon': lon})

        await message.answer(
            text=f"Отлично!\n{result['name']}\n\nИщу заведения в 10-15 минутах ходьбы...",
        )

        await send_places_on_map(message, lat, lon, state)

    except Exception as e:
        logger.error(f'Unknown error: {e}')
        await message.answer(text=f"Кажется, сегодня не работаю(\nЗагляните в другой день")

    await state.update_data()


@router.callback_query(NumbersCallbackFactory.filter(F.id))
async def callbacks_place_change_fab(
        callback: CallbackQuery,
        callback_data: NumbersCallbackFactory,
        state: FSMContext
):
    user_data = await state.get_data()
    str_place_info = await callback_str_place_info(callback_data.id)

    await callback.message.edit_caption(
        caption=str_place_info,
        reply_markup=generate_places_kb(user_data.get('places'), curr_place=callback_data.id))

    await callback.answer()

