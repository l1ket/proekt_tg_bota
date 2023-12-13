# import asyncio
import sqlite3
from aiogram import Router, F
from aiogram.filters import Command  # , StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from pars2 import ais_dnevnik
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
import datetime
# from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()
ais = ais_dnevnik()

"""
начало fsm(машина состояний)

"""


class get_data(StatesGroup):
    get_log = State()
    get_password = State()


@router.message(Command("give"))
@router.message(F.text.lower() == "передать логин и пароль")
async def taking_log(message: Message, state: FSMContext):
    await message.answer(
        text="Введите логин.", reply_markup=ReplyKeyboardRemove()
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
    kb = [
        [
            KeyboardButton(text="Главное меню")
        ],
        ]
    keyboard = ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Чтобы увидеть все команды пропишите /help"
        )

    await state.update_data(chosen_pass=message.text)
    user_data = await state.get_data()
    status = await check_stasus(user_data['chosen_log'], user_data['chosen_pass'])
    if status == 200:
        await message.answer(
            text=f"Данные сохранены.\nВаш логин: {user_data['chosen_log']},"
            f"\nВаш пароль: {user_data['chosen_pass']}.\n",reply_markup=keyboard
        )
        users_id = message.from_user.id
        await add_to_table(users_id, user_data['chosen_log'], user_data['chosen_pass'])  # функция сохранения данных
        # Сброс состояния и сохранённых данных у пользователя
        await state.clear()
    else:
        await message.answer(text='Данные не подошли, введите их еще раз.'
                             '\nНачнем с логина:')
        await state.set_state(get_data.get_log)


# async def add_to_table(user_id, login, password):
#     """
#     Асихронная функция которая сохраняет данные в БД на компе, в формате:
#     №id(возможно в БД я хз),
#     user_id, login_user, password_user, user_cookie = 1.
#     """
#     connection = sqlite3.connect('users_data.db')
#     cursor = connection.cursor()
#     cursor.execute('INSERT INTO Users (user_id, login_user, password_user, user_cookie) VALUES (?, ?, ? , ?)', (f'{user_id}', f'{login}', f'{password}', '1'))
#     connection.commit()
#     connection.close()


# async def check_stasus(login, password):
#     """
#     Проверка подходят данные пользователя или нет
#     """
#     ais = ais_dnevnik(log=login, passw=password)
#     status = ais.get_status()
#     return status


@router.callback_query(F.data == "this_week_grades")
async def start_week(callback: types.CallbackQuery):
    users_id = callback.from_user.id
    results = await check_users_in_table(users_id)
    """
    Тут жоская ловушка results == str
    """
    int_results = int(results)
    if int_results == users_id:
        await callback.answer(text='Запуск парсера...')
        text = await pars_this_week(users_id)
        await callback.message.delete()
        await callback.message.answer(text=f'{text}')
    else:
        await callback.answer(text='Ошибка:\nВы еще не передали ваши данные.')


@router.callback_query(F.data == "this_day_homework")
async def start_day(callback: types.CallbackQuery):
    users_id = callback.from_user.id
    results = await check_users_in_table(users_id)
    """
    Тут жоская ловушка results == str
    """
    int_results = int(results)
    if int_results == users_id:
        await callback.answer(text='Запуск парсера...')
        text = await get_this_homework(users_id)
        await callback.message.delete()
        await callback.message.answer(text=f'{text}')
    else:
        await callback.answer(text='Ошибка:\nВы еще не передали ваши данные.')


@router.callback_query(F.data == "1polygodie")
async def start_1_polygodie(callback: types.CallbackQuery):
    users_id = callback.from_user.id
    results = await check_users_in_table(users_id)
    """
    Тут жоская ловушка results == str
    """
    int_results = int(results)
    if int_results == users_id:
        await callback.answer(text='Запуск парсера...')
        text = await pars_1_polygodie(users_id)
        await callback.message.delete()
        await callback.message.answer(text=f'{text}')
    else:
        await callback.answer(text='Ошибка:\nВы еще не передали ваши данные.')


@router.callback_query(F.data == "2polygodie")
async def start_pars_2_polygodie(callback: types.CallbackQuery):
    await callback.answer(text='Ещё не 2 полугодие.')


@router.callback_query(F.data == "all_grades")
async def start_all_grades(callback: types.CallbackQuery):
    users_id = callback.from_user.id
    results = await check_users_in_table(users_id)
    """
    Тут жоская ловушка results == str
    """
    int_results = int(results)
    if int_results == users_id:
        await callback.answer(text='Запуск парсера...')
        text = await parsing_itog(users_id)
        await callback.message.delete()
        await callback.message.answer(text=f'{text}')
    else:
        await callback.answer(text='Ошибка:\nВы еще не передали ваши данные.')


@router.callback_query(F.data == "homeworks")
async def select_homeworks(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    date = datetime.datetime.now()
    date = date.date()
    day_week = date.weekday()
    if day_week == 0:
        day_week = 'Понедельник'
    elif day_week == 1:
        day_week = 'Вторник'
    elif day_week == 2:
        day_week = 'Среда'
    elif day_week == 3:
        day_week = 'Четверг'
    elif day_week == 4:
        day_week = 'Пятница'
    elif day_week == 5:
        day_week = 'Суббота'
    elif day_week == 6:
        day_week = 'Воскресенье'

    builder = InlineKeyboardBuilder()
    builder.button(text="Выбрать день Д/З", callback_data='...')
    builder.button(text="Д/З за сегодня", callback_data='this_day_homework')
    builder.button(text="Отмена", callback_data='back')
    builder.adjust(2)

    await callback.message.answer(text=f'Сегодня: {date}/{day_week}', reply_markup=builder.as_markup())


@router.callback_query(F.data == "all_grades_for_lesson")
async def start_pars(callback: types.CallbackQuery):
    await callback.message.answer(text='Ещё не готово.')



@router.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer('пасхалка')
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=True
    )


"""
Это надо использовать перед любым запросом на АИС(то что снизу)
"""


async def check_users_in_table(user_id):
    """
    Проверка есть пользователь в БД или нет.
    """
    res = ''
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT user_id FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        res = i[0]
    connection.close()
    if res == '':
        res = 1
    return res


async def add_to_table(user_id, login, password):
    """
    Асихронная функция которая сохраняет данные в БД на компе, в формате:
    №id(возможно в БД я хз),
    user_id, login_user, password_user, user_cookie = 1.
    """
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Users (user_id, login_user, password_user, user_cookie) VALUES (?, ?, ? , ?)', (f'{user_id}', f'{login}', f'{password}', '1'))
    connection.commit()
    connection.close()


async def check_stasus(login, password):
    """
    Проверка подходят данные пользователя или нет
    """
    ais = ais_dnevnik(log=login, passw=password)
    status = ais.get_status()
    return status


async def parsing_itog(user_id):
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT login_user, password_user FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        login = i[0]
        password = i[1]
    connection.close()
    ais = ais_dnevnik(login, password, 'Итоговые оценки')
    ais.get_cook()  # -------- РАБОТАЕТ (получаем куки)
    ais.search_all_id()
    responce = ais.select_variant()
    return responce


async def pars_this_week(user_id):
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT login_user, password_user FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        login = i[0]
        password = i[1]
    connection.close()
    ais = ais_dnevnik(login, password, 'Текущая неделя')
    ais.get_cook()  # -------- РАБОТАЕТ (получаем куки)
    ais.search_all_id()
    responce = ais.select_variant()
    return responce


async def pars_1_polygodie(user_id):
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT login_user, password_user FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        login = i[0]
        password = i[1]
    connection.close()
    ais = ais_dnevnik(login, password, '1 Полугодие')
    ais.get_cook()  # получаем куки
    ais.search_all_id()
    responce = ais.select_variant()
    return responce


async def all_subjects(user_id):
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT login_user, password_user FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        login = i[0]
        password = i[1]
    connection.close()
    ais = ais_dnevnik(login, password, 'Все предметы')
    ais.get_cook()  # получаем куки
    ais.search_all_id()
    responce = ais.select_variant()
    return responce


async def get_this_homework(user_id):
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT login_user, password_user FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        login = i[0]
        password = i[1]
    connection.close()
    ais = ais_dnevnik(login, password, 'Домашнее задание этот день')
    ais.get_cook()  # получаем куки
    ais.search_all_id()
    responce = ais.select_variant()
    return responce
