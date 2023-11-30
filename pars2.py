import requests
from bs4 import BeautifulSoup
import json
"""
ВСЕ ЭТО ПОТОМ НАДО БУДЕТ ОБЕРНУТЬ В ФУНКЦИЮ Т.К.
МЫ БУДЕМ ЮЗАТЬ ЕЕ В ОСНОВНОМ ФАЙЛЕ ТГ БОТА ЭТОТ ФАЙЛ БУДЕТ КАК ДОПОЛНЕНИЕ
"""


session = requests.Session()
# Я НЕ ЕБУ ПОЧЕМУ ДЕЛАЮТ ТАК, НО МБ ТАК ЛУЧШЕ ЧЕМ ЧЕРЕЗ
# (хотя делали и как днаписано дальше но почему то и так и так, поэтому поебать) requests.get()

# Данные для авторизации

link = 'https://dnevnik.egov66.ru/api/auth/Auth/Login'
data = json.dumps({
    "login": "DIzmestjev5f43",
    "password": "t9vMzoB&Tw"
})
headers = {'Content-type': 'application/json', 
           'Content-Length': str(len(data)), 
           'charset': 'utf-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0 (Edition Yx GX)'
}

response_for_cook = session.post(link, data=data, headers=headers).cookies.get_dict()
# print(response_for_cook)--------РАБОТАЕТ(передает куки для того чтобы продолжать работать в той же сесии)

#ээ НУ КРЧ ТУТ ПЛОТНО ЗАШЛИ В ДНЕВНИК КАЙФАНУЛИ И ПОДУМАЛИ АЧЕ ДАЛЬШЕ ТО?
# И ТУТ МЫ КАЙФУЕМ ОТ РОС РАЗРАБОВ(гении в одну страницу запихали почти все поэтому искать будет тяжело)
response2 = requests.get(url='https://dnevnik.egov66.ru/api/students', cookies=response_for_cook)
soup = BeautifulSoup(response2.text, 'lxml')
print(soup)
