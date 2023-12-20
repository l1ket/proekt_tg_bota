
import sqlite3
from pars2 import ais_dnevnik


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


async def add_to_table(user_id, acc_name, login, password, is_used):
    """
    Асихронная функция которая сохраняет данные в БД на ПК

    """
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO Users (user_id, acc_name, is_used, login_user, password_user) VALUES (?, ?, ?, ?, ?)', (f'{user_id}', f'{acc_name}', is_used, f'{login}', f'{password}')
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
    """
    Функция которая подходит для всех классов
    и получает данные за неделю
    """
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
    """
    Функция которая подходит для всех классов
    и получает данные зпо домашке за день
    """
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


async def parsing_itog(user_id):
    """
    Функция которая подходит для 10-11
    и получает данные по итоговым оценкам
    """
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


async def student_info(user_id):
    """
    Функция которая подходит для всех
    и получает данные о ученике/родителе(в будующем)
    """
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


async def get_ids():
    ids = []
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT user_id FROM Users')
    results = cursor.fetchall()
    for i in results:
        for user_id in i:
            ids.append(user_id)
    connection.close()
    return ids


async def check_login(message, user_id):
    names = []

    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    cursor.execute('SELECT acc_name FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchall()
    for i in results:
        for logins in i:
            names.append(logins)
    connection.close()

    if message in names:
        return False
    else:
        return True


async def get_all_accs(user_id):
    text = 'Аккаунты:\n\n'

    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()

    cursor.execute('SELECT acc_name, is_used FROM Users WHERE user_id = ?', (user_id,))
    names = cursor.fetchall()
    for i in names:
        for acc_inf in i:
            if acc_inf == '1':
                text += 'Используется: Да\n\n'
            elif acc_inf == '0':
                text += 'Используется: Нет\n\n'
            else:
                text += f'Имя аккаунта(не логин): {acc_inf}\n'
    connection.close()

    return text


async def check_acc_in_bd(user_id, acc_name):

    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Users WHERE user_id = ? AND acc_name = ?', (user_id, acc_name))
    connection.commit()
    connection.close()

    return ...


if __name__ == '__main__':
    print('lox')
