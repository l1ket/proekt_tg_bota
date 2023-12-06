# import asyncio
import sqlite3
from aiogram import Router, F
from aiogram.filters import Command  # , StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from pars2 import ais_dnevnik
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
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

# Переименовать
@router.message(Command(commands=["give_allpars"]))
@router.message(F.text.lower() == "итоговые оценки")
async def start_pars(message: Message):
    users_id = message.from_user.id
    results = await check_users_in_table(users_id)
    """
    Тут жоская ловушка results == str
    """
    int_results = int(results)
    if int_results == users_id:
        await message.answer(text='Запуск парсера...')
        text = await parsing_itog(users_id)
        await message.reply(text=f'{text}')
    else:
        await message.answer(text='Ошибка:\nВы еще не передали ваши данные.')


# Переименовать
@router.message(Command(commands=["this_week"]))
@router.message(F.text.lower() == "эта неделя")
async def pars_week(message: Message):
    users_id = message.from_user.id
    results = await check_users_in_table(users_id)
    """
    Тут жоская ловушка results == str
    """
    int_results = int(results)
    if int_results == users_id:
        await message.answer(text='Запуск парсера...')
        text = await pars_this_week(users_id)
        await message.reply(text=f'{text}')
    else:
        await message.answer(text='Ошибка:\nВы еще не передали ваши данные.')


# Переименовать
@router.message(Command(commands=["polygodie_1"]))
@router.message(F.text.lower() == "первое полугодие")
async def pars_1_polygodie_in_tg(message: Message):
    users_id = message.from_user.id
    results = await check_users_in_table(users_id)
    """
    Тут жоская ловушка results == str
    """
    int_results = int(results)
    if int_results == users_id:
        await message.answer(text='Запуск парсера...')
        text = await pars_1_polygodie(users_id)
        await message.reply(text=f'{text}')
    else:
        await message.answer(text='Ошибка:\nВы еще не передали ваши данные.')


@router.message(Command(commands=["polygodie_2"]))
@router.message(F.text.lower() == "второе полугодие")
async def pars_2_polygodie(message: Message):
    await message.reply(text='Еще не готово')


@router.message(F.text.lower() == "получить все оценки по конкретному предмету")
async def all_sub(message: Message):
    """
    Пока что забил т.к. очень тяжело понять откуда брать lessonid.
    """
    # users_id = message.from_user.id
    # results = await check_users_in_table(users_id)
    # """
    # Тут жоская ловушка results == str
    # """
    # int_results = int(results)
    # if int_results == users_id:
    #     await message.answer(text='Запуск парсера...')
    #     text = await all_subjects(users_id)
    #     await message.reply(text=f'{text}')
    # else:
    #     await message.answer(text='Ошибка:\nВы еще не передали ваши данные.')
    await message.answer(text='В разработке...')


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
