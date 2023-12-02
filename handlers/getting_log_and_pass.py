from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove


router = Router()

class get_data(StatesGroup):
    get_log = State()
    get_password = State()


@router.message(Command("give"))
async def taking_log(message: Message, state: FSMContext):
    await message.answer(
        text="Введите логин.",
        )
    await state.set_state(get_data.get_log)


@router.message(get_data.get_log)
async def taking_pass(message: Message, state: FSMContext):
    await state.update_data(chosen_log=message.text)
    await message.answer(
        text="Спасибо. Теперь введите пароль.",
        )
    await state.set_state(get_data.get_password)


@router.message(get_data.get_password)
async def pass_and_log_get(message: Message, state: FSMContext):
    await state.update_data(chosen_pass=message.text)
    user_data = await state.get_data()
    print(user_data)
    await message.answer(
        text=f"Ваш логин: {user_data['chosen_log']},\nВаш пароль: {user_data['chosen_pass']}.\n",
        reply_markup=ReplyKeyboardRemove()
    )
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()
