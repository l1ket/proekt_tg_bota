import requests
from bs4 import BeautifulSoup
import json

"""
ВСЕ ЭТО ПОТОМ НАДО БУДЕТ ОБЕРНУТЬ В ФУНКЦИЮ Т.К.
МЫ БУДЕМ ЮЗАТЬ ЕЕ В ОСНОВНОМ ФАЙЛЕ ТГ БОТА ЭТОТ ФАЙЛ БУДЕТ КАК ДОПОЛНЕНИЕ

"""


# Данные для авторизации
def get_cook(session):
    """
    Добавить потом получение данных логина и пароля от пользователя
    """
    link = 'https://dnevnik.egov66.ru/api/auth/Auth/Login'  # Пока хост не сменят ссылка не меняется
    data = json.dumps({"login": "DIzmestjev5f43",
                       "password": "t9vMzoB&Tw"
                                                })
    headers = {'Content-type': 'application/json',
               'Content-Length': str(len(data)),
               'charset': 'utf-8',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0 (Edition Yx GX)'
}

    response_for_cook = session.post(link, data=data,
                                     headers=headers).cookies.get_dict()
    return response_for_cook


def find_itog_ocenki():
    # ПЛОТНО ИЩЕМ НАЗВАНИЯ ПРЕДМЕТОВ (СУКИ ВСЕ В JSON ОБЬЕКТ ОБЕРНУЛИ)
    response2 = requests.get(
        url='https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId=3666e57b-c830-42bb-a9ae-4332edf2020c&subjectId=00000000-0000-0000-0000-000000000000&studentId=b0ccd038-8de2-4c12-913b-a1dcfb9bcfef',
        cookies=response_for_cook)
    soup = BeautifulSoup(response2.text, 'lxml')
    dict_lessons = json.loads(soup.text)  # Преобразовал str в dict

    find_lessons = dict_lessons['periodGradesTable']
    find_lessons2 = find_lessons['disciplines']  # --- (type - list)
    # print(find_lessons2)  # ---- если надо будет чекнуть че тут лежит
    itog = ''

    for less in find_lessons2:
        name_less = less['name']
        ocenka = less['avarageGrade']
        itog += str(f'{name_less}: {ocenka}\n')
    return print(itog)


session = requests.Session()  # запуск сессии Я НЕ ЕБУ ПОЧЕМУ ДЕЛАЮТ ТАК, НО МБ ТАК ЛУЧШЕ ЧЕМ ЧЕРЕЗ requests.get(), (хотя делали и как написано но почему то и так и так, поэтому поебать)
response_for_cook = get_cook(session)  # -------- РАБОТАЕТ (передает куки для того чтобы продолжать работать в той же сесии)
find_itog_ocenki()  # Работает

"""
Еще надо будет все print в конце функций заменить на return
print -> return
"""
