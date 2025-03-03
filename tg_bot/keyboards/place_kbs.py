from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NumbersCallbackFactory(CallbackData, prefix="place"):
    id: int
    name: str
    page: int


def generate_places_kb(places, curr_place=None):
    builder = InlineKeyboardBuilder()

    for index, place in enumerate(places):
        builder.button(
            text=f"📍 {index+1}. {place['title']}" if curr_place == place['id'] else f"{index+1}. {place['title']}",
            callback_data=NumbersCallbackFactory(id=place['id'], name=place['title'], page=1)
        )

    # if paginator['prev_page']:
    #     builder.button(
    #         text="Назад", callback_data=NumbersCallbackFactory(id=0, name='show prev', page=curr_page-1)
    #     )
    #
    # if paginator['next_page']:
    #     builder.button(
    #         text="Дальше", callback_data=NumbersCallbackFactory(id=0, name='show next', page=curr_page+1)
    #     )
    builder.adjust(3)
    return builder.as_markup()
