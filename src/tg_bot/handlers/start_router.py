from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.tg_bot.fsm import LocationState
from src.tg_bot.keyboards.kbs import location_kb

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    # TODO: move weather here with remembered city
    await message.answer(
        "Привет!\nЯ бот, который поможет найти, где выпить кофе!"
        "\n\nНапиши свой город или отправь геолокацию, чтобы я смог найти тебя",
        reply_markup=location_kb()
    )
    await state.set_state(LocationState.choosing_city)


@start_router.message(F.text == '❌ Остановить сценарий')
@start_router.message(Command("clear"))
async def stop_fsm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Сценарий остановлен. Чтобы начать снова отправьте /start",
        reply_markup=types.ReplyKeyboardRemove()
    )


@start_router.message(StateFilter(None))
async def handle_incorrectly(message: Message):
    await message.answer(
        text="Сценарий пуст! Чтобы начать снова, введите любую команду, например /start\n"
    )
