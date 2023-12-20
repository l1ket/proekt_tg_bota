import sqlite3
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from pars2 import ais_dnevnik

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    builder = InlineKeyboardBuilder()
    builder.button(text="Аккаунты", callback_data='accs')
    builder.button(text="АИС(дневник)", callback_data='ais')
    builder.adjust(2)

    await message.answer(
        text="Привет этот бот получет информацию из электронного "
        "дневника свердловской области!\n"
        "Воспользуйтесь кнопками.\nВерсия бота: v0.2.1(beta)",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == 'start_back')
async def cmd_main(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()

    builder = InlineKeyboardBuilder()
    builder.button(text="Аккаунты", callback_data='accs')
    builder.button(text="АИС(дневник)", callback_data='ais')
    builder.adjust(2)

    await callback.message.answer(
        text="Главное меню",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    builder = InlineKeyboardBuilder()
    builder.button(text="1-9", callback_data='first_nine')
    builder.button(text="10-11", callback_data='ten_eleven')
    builder.adjust(2)

    await callback.message.answer(
        text="Выберите свой класс:", reply_markup=builder.as_markup()
        )


@router.callback_query(F.data == "ais")
async def after_main(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.message.from_user.id
    inf = await student_info(user_id)
    if inf is False:
        await callback.message.answer(
            text='Вы еще не предали ваши данные от аккаунта, '
            'поэтому при попытке что-то запустить ничего не сработает'
            )
    else:
        await callback.message.answer(text=f'Текущий аккаунт:\n{inf}')

    builder = InlineKeyboardBuilder()
    builder.button(text="1-9", callback_data='first_nine')
    builder.button(text="10-11", callback_data='ten_eleven')
    builder.adjust(2)

    await callback.message.answer(
        text="Выберите свой класс:", reply_markup=builder.as_markup()
        )


@router.callback_query(F.data == "accs")
async def accs(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    builder = InlineKeyboardBuilder()
    builder.button(text="Просмотреть все акаунты", callback_data='check_acs')
    builder.button(text="Выбрать используемый аккаунт", callback_data='select_ac')
    builder.button(text="Добавить аккаунт", callback_data='add_ac')
    builder.button(text="Удалить аккаунт", callback_data='del_ac')
    builder.button(text="Назад", callback_data='start_back')
    builder.adjust(2)

    await callback.message.answer(
        text="Выберите действие для аккаунтов:",
        reply_markup=builder.as_markup()
        )


# default_state - это то же самое, что и StateFilter(None)
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стейт сбрасывать не нужно, удалим только данные

    builder = InlineKeyboardBuilder()
    builder.button(text="Главное меню", callback_data='start_back')
    builder.adjust(1)

    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=builder.as_markup()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):

    builder = InlineKeyboardBuilder()
    builder.button(text="Главное меню", callback_data='start_back')
    builder.adjust(1)

    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=builder.as_markup()
    )


async def student_info(user_id):
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT login_user, password_user FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    if results == []:
        return False
    for i in results:
        login = i[0]
        password = i[1]
    connection.close()
    ais = ais_dnevnik(login, password, 'Данные о аккаунте')
    ais.get_cook()  # получаем куки
    ais.search_all_id()
    responce = ais.select_variant()
    return responce
