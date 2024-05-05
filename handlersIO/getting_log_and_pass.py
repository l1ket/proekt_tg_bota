import sqlite3

from aiogram import Router, F

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from parsIO import AISdnevnik

router = Router()

"""
начало fsm(машина состояний)
"""


class get_data(StatesGroup):
    get_log = State()
    get_password = State()


@router.message(Command("give"))
@router.message(F.text.lower() == "добавить аккаунт")
async def taking_log(message: Message, state: FSMContext):
    kb = [[KeyboardButton(text="Главное меню")],]
    keyboard = ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Чтобы вернуться в главное меню пропишите /main или /start")

    await message.answer(
        text="Введите логин.", reply_markup=keyboard
        )
    await state.set_state(get_data.get_log)


@router.message(get_data.get_log)
async def taking_pass(message: Message, state: FSMContext):
    await state.update_data(chosen_log=message.text)

    kb = [[KeyboardButton(text="Главное меню")],]
    keyboard = ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Чтобы вернуться в главное меню пропишите /main или /start")

    await message.answer(
        text="Спасибо. Теперь введите пароль.",
        reply_markup=keyboard
        )
    await state.set_state(get_data.get_password)


@router.message(get_data.get_password)
async def pass_and_log_get(message: Message, state: FSMContext):
    kb = [[KeyboardButton(text="Главное меню")],]
    keyboard = ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Чтобы вернуться в главное меню пропишите /main или /start")

    await message.answer(text='Проверка аккаунта...')
    await state.update_data(chosen_pass=message.text)
    user_data = await state.get_data()
    logins = await check_acc_in_bd(user_id=message.from_user.id)

    if user_data['chosen_log'] == '123':
        await message.answer(text='Этот аккаунт зарезервирован системой.\n'
                             'Начнем с начала. Введите логин.')
        await state.clear()
        await state.set_state(get_data.get_log)
    else:
        if user_data['chosen_log'] in logins:
            await message.answer(
                text='Аккаунт с таким логином у вас уже есть, начнём с начала.'
                '\nВведите логин:',
                reply_markup=keyboard
                )
            await state.clear()
            await state.set_state(get_data.get_log)
        else:
            status = await check_stasus(user_data['chosen_log'], user_data['chosen_pass'])

            if status is True:
                users_id = message.from_user.id
                await add_user(
                    user_id=users_id,
                    password_user=user_data['chosen_pass'],
                    main_login=user_data['chosen_log']
                    )
                await message.answer(
                    text=f"Данные сохранены.\nВаш логин: {user_data['chosen_log']},"
                    f"\nВаш пароль: {user_data['chosen_pass']}.\n", reply_markup=keyboard
                )
                await state.clear()
            else:
                await message.answer(
                    text='Данные не подошли, введите их еще раз.'
                         '\nНачнем с логина:',
                         reply_markup=keyboard
                         )
                await state.clear()
                await state.set_state(get_data.get_log)


"""             Функции             """


async def check_users_in_table(user_id):
    """
    Проверка есть пользователь в БД или нет.
    """
    res = ''
    connection = sqlite3.connect('accs.db')
    cursor = connection.cursor()
    cursor.execute('SELECT user_id FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        res = i[0]
    connection.close()
    if res == '':
        res = 1
    return res


async def get_default_credentials(us_id) -> tuple:
    # Connect to accs.db
    conn_accs = sqlite3.connect('accs.db')
    cursor_accs = conn_accs.cursor()

    # Get default user_id from accs.db
    cursor_accs.execute("SELECT main_login FROM Users WHERE user_id = ?", (us_id,))
    default_user_log = cursor_accs.fetchone()[0]

    # Connect to accs_info.db
    conn_accs_info = sqlite3.connect('accs_info.db')
    cursor_accs_info = conn_accs_info.cursor()

    # Get login and password from accs_info.db using default user_id
    cursor_accs_info.execute("SELECT login_user, password_user FROM Users WHERE login_user = ?", (default_user_log,))
    login, password = cursor_accs_info.fetchone()

    # Close connections
    conn_accs.close()
    conn_accs_info.close()

    return login, password


async def add_user(user_id, password_user, main_login):
    connection = sqlite3.connect('accs.db')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO Users (user_id, main_login)
        VALUES (?, ?)
    ''', (user_id, main_login))
    connection.commit()
    connection.close()

    connection = sqlite3.connect('accs_info.db')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO Users (user_id, login_user, password_user)
        VALUES (?, ?, ?)
    ''', (user_id, main_login, password_user))
    connection.commit()
    connection.close()


async def check_stasus(login, password) -> bool:
    """
    Проверка подходят данные пользователя или нет
    """
    ais = AISdnevnik(log=login, passw=password)
    status = await ais.check_acc()
    return status


async def check_acc_in_bd_accs(user_id) -> bool:
    logins = []
    connection = sqlite3.connect('accs.db')
    cursor = connection.cursor()
    cursor.execute('SELECT user_id FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        logins.append(i[0])
    if logins != []:
        return True
    else:
        return False


async def check_acc_in_bd(user_id) -> list:
    logins = []
    connection = sqlite3.connect('accs_info.db')
    cursor = connection.cursor()
    cursor.execute('SELECT login_user FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        logins.append(i[0])
    return logins


async def return_accs(user_id) -> list[tuple]:
    accs = []
    connection = sqlite3.connect('accs_info.db')
    cursor = connection.cursor()
    cursor.execute('SELECT login_user, password_user FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        accs.append(i)
    return accs


async def return_main_login(user_id) -> str:
    connection = sqlite3.connect('accs.db')
    cursor = connection.cursor()
    cursor.execute('SELECT main_login FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        return i[0]


async def change_main_login(user_id, login) -> str:
    connection = sqlite3.connect('accs.db')
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE Users
        SET main_login = ?
        WHERE user_id = ?
    ''', (login, user_id))
    connection.commit()
    connection.close()


async def return_user_ids() -> list:
    ids = []
    connection = sqlite3.connect('accs.db')
    cursor = connection.cursor()
    cursor.execute('SELECT user_id FROM Users')
    results = cursor.fetchall()
    for i in results:
        ids.append(i[0])
    return ids