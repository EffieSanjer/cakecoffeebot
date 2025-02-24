from aiogram import Router, F, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from backend.models import Place
from services.geolocation import get_location, get_map_image, get_place_index
from services.weather import get_weather
from use_cases.places_use_case import place_use_case

router = Router()


# places callbacks
class NumbersCallbackFactory(CallbackData, prefix="place"):
    id: int
    name: str
    page: int


def get_keyboard_fab(paginator, curr_place=None):
    builder = InlineKeyboardBuilder()

    curr_page = paginator['page']
    total = len(paginator['places'])

    for i, place in enumerate(paginator['places']):
        if type(place) is dict:
            place = Place(**place)

        index = get_place_index(curr_page, total, i+1)
        builder.button(
            text=f"📍 {index}. {place.title}" if curr_place == place.id else f"{index}. {place.title}",
            callback_data=NumbersCallbackFactory(id=place.id, name=place.title, page=curr_page)
        )

    if paginator['prev_page']:
        builder.button(
            text="Назад", callback_data=NumbersCallbackFactory(id=0, name='show prev', page=curr_page-1)
        )

    if paginator['next_page']:
        builder.button(
            text="Дальше", callback_data=NumbersCallbackFactory(id=0, name='show next', page=curr_page+1)
        )
    builder.adjust(3)
    return builder.as_markup()


class LocationState(StatesGroup):
    choosing_city = State()
    choosing_address = State()
    showing_places = State()
    creating_place = State()
    rating_place = State()


@router.message(LocationState.choosing_city, F.location)
async def handle_geolocation(message: Message, state: FSMContext, today: str):
    lat = message.location.latitude
    lon = message.location.longitude

    weather = get_weather(lat=lat, lon=lon)
    await state.update_data(city=weather['city'])

    location = get_location(city=weather['city'], lat=lat, lon=lon)
    await state.update_data(address={'lat': lat, 'lon': lon})

    await state.set_state(LocationState.choosing_address)

    await message.answer(
        f"Твой адрес: {location['name']}!\n "
        f"Сегодня {today}, {weather['weather']}, {weather['temp']}℃.\n"
        f"Ищу заведения в 10-15 минутах ходьбы...",
        reply_markup=types.ReplyKeyboardRemove()
    )

    places = await place_use_case.get_places_by_point(lat, lon)

    map_image = get_map_image(places, lat, lon)
    if map_image is not None:
        await message.answer_photo(
            photo=map_image,
            caption=f"Вот список ближайших мест:",
            reply_markup=get_keyboard_fab(places)
        )
    else:
        await message.answer(text=f"Вот список ближайших мест:", reply_markup=get_keyboard_fab(places))


@router.message(LocationState.choosing_city, F.text)
async def handle_text_location(message: Message, state: FSMContext, today: str):
    city = message.text
    await state.update_data(city=city)

    try:
        weather = get_weather(city=city)

        await message.answer(
            f"Твой город: {city}!\n"
            f"Сегодня {today}, {weather['weather']}, {weather['temp']}℃.\n"
            f"Отличный день, чтобы прогуляться с кофе!",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except:
        await message.answer(
            "К сожалению, я не вижу какая сегодня погода, но все равно могу помочь!",
            reply_markup=types.ReplyKeyboardRemove()
        )

    await message.answer("Начнем с простого: в район какого метро Вы хотите отправиться?")
    await state.set_state(LocationState.choosing_address)


@router.message(LocationState.choosing_address, F.text)
async def handle_subway(message: Message, state: FSMContext):
    subway = message.text
    await state.update_data(address=subway)

    user_data = await state.get_data()
    try:
        result = get_location(city=user_data.get('city'), location=f'станция метро {subway}')
        lat, lon = result['geometry']['lat'], result['geometry']['lng']
        await state.update_data(address={'lat': lat, 'lon': lon})

        await message.answer(
            text=f"Отлично!\n{result['name']}\nИщу заведения в 10-15 минутах ходьбы...",
        )
        places = await place_use_case.get_places_by_point(lat, lon)

        map_image = get_map_image(places, lat, lon)
        if map_image is not None:
            await message.answer_photo(
                photo=map_image,
                caption=f"Вот список ближайших мест:",
                reply_markup=get_keyboard_fab(places)
            )
        else:
            await message.answer(text=f"Вот список ближайших мест:", reply_markup=get_keyboard_fab(places))

    except Exception as e:
        await message.answer(text=f"Кажется, сегодня не работаю(\nЗагляните в другой день")

    await state.update_data()


@router.message(F.text)
async def handle_incorrectly(message: Message):
    await message.answer(
        text="Я Вас не понял, давайте попробуем еще раз.\n"
             "Пожалуйста, напишите еще раз."
    )
