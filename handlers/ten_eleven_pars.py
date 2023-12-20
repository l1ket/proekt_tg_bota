import sqlite3
from aiogram import Router, F
from pars2 import ais_dnevnik
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

router = Router()


@router.callback_query(F.data == "ten_eleven")
async def ten_eleven_pars(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    builder = InlineKeyboardBuilder()

    builder.button(text="Эта неделя", callback_data='this_week_grades')
    builder.button(text="Домашние задания", callback_data='homeworks')
    builder.button(text="Первое полугодие", callback_data='1polygodie_11')
    builder.button(text="Второе полугодие", callback_data='2polygodie_11')
    builder.button(text="Итоговые оценки", callback_data='all_grades_11')
    # builder.button(text="Получить все оценки по конкретному предмету(в разработке...)", callback_data='all_grades_for_lesson_11')

    builder.adjust(1)
    await callback.message.answer(
        text="Выберите вариант ниже:", reply_markup=builder.as_markup()
        )


@router.callback_query(F.data == "1polygodie_11")
async def start_1_polygodie(callback: types.CallbackQuery):
    users_id = callback.from_user.id
    results = await check_users_in_table(users_id)
    int_results = int(results)  # results == str

    if int_results == users_id:
        await callback.answer(text='Запуск парсера...')
        text = await pars_1_polygodie(users_id)
        await callback.message.delete()
        await callback.message.answer(text=f'{text}')
    else:
        await callback.answer(text='Ошибка:\nВы еще не передали ваши данные.')


@router.callback_query(F.data == "2polygodie_11")
async def start_pars_2_polygodie(callback: types.CallbackQuery):
    await callback.answer(text='Ещё не 2 полугодие.')


@router.callback_query(F.data == "all_grades_11")
async def start_all_grades(callback: types.CallbackQuery):
    users_id = callback.from_user.id
    results = await check_users_in_table(users_id)
    int_results = int(results)  # results == str

    if int_results == users_id:
        await callback.answer(text='Запуск парсера...')
        text = await parsing_itog(users_id)
        await callback.message.delete()
        await callback.message.answer(text=f'{text}')
    else:
        await callback.answer(text='Ошибка:\nВы еще не передали ваши данные.')


@router.callback_query(F.data == "all_grades_for_lesson_11")
async def start_pars(callback: types.CallbackQuery):
    await callback.answer(text='Ещё не готово')


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
