"""
Файл для получения общих данных
которые подходят всем
"""
import sqlite3
from aiogram import Router, F
from pars2 import ais_dnevnik
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
import datetime

router = Router()
ais = ais_dnevnik()


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

    await callback.message.answer(text=f'Сегодня: {date}/{day_week}',
                                  reply_markup=builder.as_markup())


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


async def add_to_table(user_id, acc_name, login, password):
    """
    Асихронная функция которая сохраняет данные в БД на ПК

    """
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO Users (user_id, acc_name, is_used, login_user, password_user) VALUES (?, ?, ?, ?, ?)', (f'{user_id}', f'{acc_name}', True, f'{login}', f'{password}')
        )
    connection.commit()
    connection.close()


async def check_accs(user_id):
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(user_id) FROM Users WHERE user_id = ?', (f'{user_id}',))
    data = cursor.fetchone()[0]
    connection.commit()
    connection.close()
    return data


async def check_stasus(login, password):
    """
    Проверка подходят данные пользователя или нет
    """
    ais = ais_dnevnik(log=login, passw=password)
    status = ais.get_status()
    return status


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
