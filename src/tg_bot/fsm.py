from aiogram.fsm.state import StatesGroup, State


class LocationState(StatesGroup):
    choosing_city = State()
    choosing_address = State()
    showing_places = State()
    creating_place = State()
    rating_place = State()

