import locale

from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from  services.schedule import get_closest_events, add_event

router = Router()


def tickets_button(events):
    builder = InlineKeyboardBuilder()
    for event in events:
        if event.tickets is not None:
            builder.row(types.InlineKeyboardButton(
                text=f"🎟 {event.title}", url=event.tickets)
            )
    return builder.as_markup(resize_keyboard=True)


@router.message(Command("schedule"))
async def cmd_get_schedule(message: types.Message):
    events = get_closest_events()
    locale.setlocale(locale.LC_TIME, "ru_RU")
    nl = '\n'.join(list(map(lambda x: f"\n<b>{x.title}</b>\n"
                                      f"{x.datetime.strftime('%d.%m.%Y %H:%M (%A)')}\n"
                                      f"{x.address}\n"
                                      f"{x.description if x.description is not None else ''}", events)))

    await message.answer(f"Расписание на ближайший месяц:\n{nl}", reply_markup=tickets_button(events))


class EventState(StatesGroup):
    creating_event = State()


@router.message(Command("event"))
async def cmd_add_event(message: types.Message, state: FSMContext):
    await message.answer(f"Добавьте новое мероприятие в формате:\n"
                         f"Название\nДата и время (дд.мм.гггг чч:мм)\nАдрес\n"
                         f"Описание\n"
                         f"Ссылка на эл. билет (если больше одной, остальные в описание)\n")

    await state.set_state(EventState.creating_event)


@router.message(EventState.creating_event, F.text)
async def creating_event(message: types.Message, state: FSMContext):
    msg = message.text
    new_event = add_event(msg.split('\n'))

    await message.answer(f"Добавлено мероприятие:\n"
                         f"\n{new_event}")
    await state.clear()


