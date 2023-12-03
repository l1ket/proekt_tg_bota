from aiogram import Router  # , F
from aiogram.filters import Command  # , StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from pars2 import ais_dnevnik

router = Router()
ais = ais_dnevnik()

"""
начало fsm(машина состояний)

"""


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
    ais_dnevnik(user_data['chosen_log'], user_data['chosen_pass'])
    status = ais.get_cook()
    print(status)
    if status == 200:
        await message.answer(
            text=f"Данные сохранены.\nВаш логин: {user_data['chosen_log']},"
            "\nВаш пароль: {user_data['chosen_pass']}.\n",
        )
        # Сброс состояния и сохранённых данных у пользователя
        await state.clear()
    else:
        await message.answer(text='Данные не подошли, введите их еще раз.\nНачнем с логина:')
        await state.set_state(get_data.get_log)
"""
Не законченна проверка данных на настоящие,
данные не передаются в функцию...
ДОДЕЛАТЬ

"""


@router.message(Command(commands=["give_allpars"]))
async def cmd_start(message: Message):
    await message.answer(
        text="Запускаем парсинг..."
    )
    await start_pars()


async def start_pars():
    response_for_cook = ais.get_cook()
    if response_for_cook is False:
        bad_pars()
    else:
        stid = ais.search_id(response_for_cook)
        ais.all_ocenki()


# @router.message()
# async def bad_pars(message: Message):
#     await message.answer(text='Данные не подошли, запустите команду /give еще раз.')
