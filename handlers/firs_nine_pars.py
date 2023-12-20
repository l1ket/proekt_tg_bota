import sqlite3
from pars2 import ais_dnevnik
from aiogram import F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

router = Router()


@router.callback_query(F.data == "first_nine")
async def first_nine_pars(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    builder = InlineKeyboardBuilder()

    builder.button(text="Эта неделя", callback_data='this_week_grades')
    builder.button(text="Домашние задания", callback_data='homeworks')
    builder.button(text="Четверти", callback_data='period_grades')
    builder.button(text="Итоговые оценки", callback_data='all_grades_9')
    # builder.button(text="Получить все оценки по конкретному предмету(в разработке...)", callback_data='all_grades_for_lesson')

    builder.adjust(1)
    await callback.message.answer(
        text="Выберите вариант ниже:", reply_markup=builder.as_markup()
        )


@router.callback_query(F.data == "period_grades")
async def select_periods(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    builder = InlineKeyboardBuilder()

    builder.button(text="1 Четверть", callback_data='first')
    builder.button(text="2 Четверть", callback_data='second')
    builder.button(text="3 Четверть", callback_data='third')
    builder.button(text="4 Четверть", callback_data='four')

    builder.adjust(1)
    await callback.message.answer(
        text="Выберите вариант ниже:", reply_markup=builder.as_markup()
        )


@router.callback_query(F.data == "all_grades_9")
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
