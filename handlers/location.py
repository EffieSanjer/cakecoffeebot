import json

from aiogram import Router, F, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from decouple import config

from models import Place
from services.geolocation import get_location, get_map_image
from services.place_generation import get_places, get_place_info
from services.weather import get_weather

router = Router()


# places callbacks
class NumbersCallbackFactory(CallbackData, prefix="place"):
    id: int
    name: str


def get_keyboard_fab(places, curr_place=None):
    builder = InlineKeyboardBuilder()
    for i, place in enumerate(places):
        if type(place) is dict:
            place = Place(**place)
        builder.button(
            text=f"📍 {i+1}. {place.title}" if curr_place == place.id else f"{i+1}. {place.title}",
            callback_data=NumbersCallbackFactory(id=place.id, name=place.title)
        )
    builder.button(
        text="Показать еще", callback_data=NumbersCallbackFactory(id=0, name='show more')
    )
    builder.adjust(3)
    return builder.as_markup()


class LocationState(StatesGroup):
    choosing_city = State()
    choosing_address = State()
    showing_places = State()


@router.message(LocationState.choosing_city, F.location)
async def handle_geolocation(message: Message, state: FSMContext, today: str):
    lat = message.location.latitude
    lon = message.location.longitude

    weather = get_weather(lat=lat, lon=lon)
    await state.update_data(city=weather['city'])

    location = get_location(city=weather['city'], lat=lat, lon=lon)
    await state.update_data(address=location)

    await state.set_state(LocationState.choosing_address)

    await message.answer(f"Твой адрес: {location}!\n"
                         f"Сегодня {today}, {weather['weather']}, {weather['temp']}℃.\n"
                         f"Ищу заведения в 10-15 минутах ходьбы...",
                         reply_markup=types.ReplyKeyboardRemove())

    places = get_places(location['geometry']['lat'], location['geometry']['lng'])

    map_image = get_map_image(places, location['geometry']['lat'], location['geometry']['lng'])
    if map_image is not None:
        await message.answer_photo(
            photo=map_image,
            caption=f"Вот список ближайших мест:",
            reply_markup=get_keyboard_fab(places))
    else:
        await message.answer(text=f"Вот список ближайших мест:", reply_markup=get_keyboard_fab(places))


@router.message(LocationState.choosing_city, F.text)
async def handle_text_location(message: Message, state: FSMContext, today: str):
    city = message.text
    await state.update_data(city=city)

    try:
        weather = get_weather(city=city)

        await message.answer(f"Твой город: {city}!\n"
                             f"Сегодня {today}, {weather['weather']}, {weather['temp']}℃.\n"
                             f"Отличный день, чтобы прогуляться с кофе!",
                             reply_markup=types.ReplyKeyboardRemove())
    except:
        await message.answer("К сожалению, я не вижу какая сегодня погода, но все равно могу помочь!",
                             reply_markup=types.ReplyKeyboardRemove())

    await message.answer("Начнем с простого: в район какого метро Вы хотите отправиться?")
    await state.set_state(LocationState.choosing_address)


@router.message(LocationState.choosing_address, F.text)
async def handle_subway(message: Message, state: FSMContext):
    subway = message.text
    await state.update_data(address=subway)

    user_data = await state.get_data()
    try:
        result = get_location(city=user_data.get('city'), location=f'станция метро {subway}')

        await message.answer(
            text=f"Отлично!\n{result['name']}\nИщу заведения в 10-15 минутах ходьбы...",
        )
        places = get_places(result['geometry']['lat'], result['geometry']['lng'])
        await state.set_state(LocationState.showing_places)
        await state.update_data(places=[{'id': _.id, 'title': _.title} for _ in places])

        map_image = get_map_image(places, result['geometry']['lat'], result['geometry']['lng'])
        if map_image is not None:
            await message.answer_photo(
                photo=map_image,
                caption=f"Вот список ближайших мест:",
                reply_markup=get_keyboard_fab(places))
        else:
            await message.answer(text=f"Вот список ближайших мест:", reply_markup=get_keyboard_fab(places))

    except:
        await message.answer(text=f"Кажется, сегодня не работаю(\nЗагляните в другой день")

        if config('DEBUG'):
            await message.answer(text=f"Запускаю тестовый режим для адреса:\n"
                                      f"станция метро 'Чернышевская', Санкт-Петербург")

            places = get_places(59.944502, 30.359801)
            await state.set_state(LocationState.showing_places)
            await state.update_data(places=[{'id': _.id, 'title': _.title} for _ in places])

            map_image = get_map_image(places, 59.944502, 30.359801)
            if map_image is not None:
                await message.answer_photo(
                    photo=map_image,
                    caption=f"Вот список ближайших мест:",
                    reply_markup=get_keyboard_fab(places))
            else:
                await message.answer(text=f"Вот список ближайших мест:", reply_markup=get_keyboard_fab(places))

    await state.update_data()


@router.callback_query(NumbersCallbackFactory.filter(F.id))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory,
        state: FSMContext
):
    user_data = await state.get_data()
    await callback.message.edit_caption(
        caption=get_place_info(callback_data.id),
        reply_markup=get_keyboard_fab(user_data.get('places'), callback_data.id))
    await callback.answer()


@router.callback_query(NumbersCallbackFactory.filter(F.id == 0))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    await callback.message.edit_text(f"Загружаю еще..")
    await callback.answer()


@router.message()
async def handle_subway_incorrectly(message: Message):
    await message.answer(
        text="Я Вас не понял, давайте попробуем еще раз.\n"
             "Пожалуйста, напишите еще раз."
    )
