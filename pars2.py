import requests
from bs4 import BeautifulSoup
import json

"""

ВСЕ ЭТО ПОТОМ НАДО БУДЕТ ОБЕРНУТЬ В ФУНКЦИЮ Т.К.
МЫ БУДЕМ ЮЗАТЬ ЕЕ В ОСНОВНОМ ФАЙЛЕ ТГ БОТА ЭТОТ ФАЙЛ БУДЕТ КАК ДОПОЛНЕНИЕ

"""
log = 'DIzmestjev5f43'
passw = 't9vMzoB&Tw'


def get_cook(log,passw):
    """

    Лутаем куки.
    Добавить потом получение данных логина и пароля от пользователя

    """
    link = 'https://dnevnik.egov66.ru/api/auth/Auth/Login'  # Пока хост не сменят ссылка не меняется
    data = json.dumps({"login": f"{log}",
                       "password": f"{passw}"
                                                })
    headers = {'Content-type': 'application/json',
               'Content-Length': str(len(data)),
               'charset': 'utf-8',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0 (Edition Yx GX)'
}

    response_for_cook = requests.post(link, data=data,
                                     headers=headers).cookies.get_dict()  # Получили куки
    return response_for_cook


def search_id(response_for_cook):
    """
    оказывается в дневнике у каждого ученика есть свой id
    и он добавляется в ссылку перед тем как что то открывать,
    но это даже в браузерной ссылке не увидеть
    поэтому все что идет дальше это поиск этого id

    """

    response_for_url = requests.get(url='https://dnevnik.egov66.ru/api/students', cookies=response_for_cook).text
    response_for_url_str = json.loads(response_for_url)
    response_for_url_str = response_for_url_str['students']
    for stid in response_for_url_str:
        stid = stid['id']
    return stid


"""

так же у каждого предмета есть id
поэтому его также надо найти

"""


def find_itog_ocenki(response_for_cook, stid):
    """
    вообщем в ссылке нужно 4 элемента:
    schoolYear = нет
    periodId = есть
    subjectId = нет
    studentId = нет

    """
    response2 = requests.get(
        url=f'https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId=3666e57b-c830-42bb-a9ae-4332edf2020c&subjectId=00000000-0000-0000-0000-000000000000&studentId={stid}',
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


response_for_cook = get_cook(log, passw)  # -------- РАБОТАЕТ (полчуаем куки)
stid = search_id(response_for_cook)
find_itog_ocenki(response_for_cook, stid)  # Работает(уже нет)(починил)



"""

Еще надо будет все print в конце функций заменить на return
print -> return

"""
