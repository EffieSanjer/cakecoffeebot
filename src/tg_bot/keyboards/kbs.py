from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def location_kb():
    kb_list = [
        [KeyboardButton(text="Санкт-Петербург")],
        [KeyboardButton(text="Москва")],
        [KeyboardButton(text="Поделиться местоположением", request_location=True)]
    ]

    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def stop_fsm():
    kb_list = [
        [KeyboardButton(text="❌ Остановить сценарий")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Для того чтоб остановить сценарий FSM нажми на кнопку"
    )
