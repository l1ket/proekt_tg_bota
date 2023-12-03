"""
Парсер данных для бота(beta-сейчас стабильная)\n
Возможности:\n
Получать данные итоговых оценок и первой четверти\n
Есть проверка на правильные логин и пароль.
Есть получение данных за текущую неделю

"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time


class ais_dnevnik:
    def __init__(self, log='', passw='', variant='Текущая неделя', **period) -> None:
        self.password = passw
        self.variant = variant
        self.dict_periods = period

    def get_cook(self):
        """

        Лутаем куки.
        Добавить потом получение данных логина и пароля от пользователя

        """
        link = 'https://dnevnik.egov66.ru/api/auth/Auth/Login'  # Пока хост не сменят ссылка не меняется(хост сменили в этот ноябрь, так что могут еще раз, хотя хост уже только на нашу область так что врятли)
        data = json.dumps({"login": f"{self.login}",
                        "password": f"{self.password}"})

        headers = {'Content-type': 'application/json',
                    'Content-Length': str(len(data)),
                    'charset': 'utf-8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0 (Edition Yx GX)'}

        response_for_cook = requests.post(link, data=data,
                                        headers=headers).status_code  # Проверка подошли данные или нет
        if response_for_cook == 200:
            response_for_cook = requests.post(link, data=data,
                                        headers=headers).cookies
        else:
            print('ne norm')
            print(self.login, self.password)
            response_for_cook == False
        return response_for_cook

    def search_all_id(self, response_for_cook):
        """
        Оказывается в дневнике:\n
        у каждого ученика есть свой id\n
        у каждого урока есть свой id\n
        у каждого периода есть свой id.\n
        И они добавляются в ссылку перед тем как что то открывать,
        но это даже в браузерной ссылке не увидеть,
        поэтому все что идет в этой функции это поиск этих id\n
        schoolYear = нет(его либо нельзя найти либо я плохо искал,
        так что будем сами ставить года)\n
        periodId = есть\n
        subjectId = нет
        (используется в случае если перейти во вкладку отдельного предмета)\n
        studentId = есть\n

        """

        response_for_url = requests.get(url='https://dnevnik.egov66.ru/api/students', cookies=response_for_cook).text
        response_for_url_str = json.loads(response_for_url)
        response_for_url_str = response_for_url_str['students']
        for stid in response_for_url_str:
            stid = stid['id']

        response_for_period = requests.get(url='https://dnevnik.egov66.ru/api/estimate/periods?schoolYear=2023&studentId=b0ccd038-8de2-4c12-913b-a1dcfb9bcfef', cookies=response_for_cook).text
        response_for_period_str = json.loads(response_for_period)
        response_for_period_str = response_for_period_str['periods']
        for i in response_for_period_str:
            name_period = i['name']
            id_period = i['id']
            self.dict_periods[name_period] = id_period
        return stid

    def find_itog_ocenki(self):
        """
        Получаем буквально все оценки из вкладки 'Итоговые оценки'\n
        Кроме оценок экзамен и похожих(потому что не целесообразно)
        Вообщем в ссылке нужно 4 элемента(хотя мб нет, получается и без них):\n
        schoolYear = нет(его либо нельзя найти либо я плохо искал,
        так что будем сами ставить года)\n
        periodId = есть\n
        subjectId = нет
        (используется в случае если перейти во вкладку отдельного предмета)\n
        studentId = есть\n
        (самая долгая функция в плане ожидания по времени - хз почему так)
        """
        itog_ocenki_1 = 'Итоговые оценки за 1 полугодие(если стоит None или 0, то учителя еще не выставили):\n\n'
        itog_ocenki_2 = 'Итоговые оценки за 2 полугодие(если стоит None или 0, то учителя еще не выставили):\n\n'
        perid = self.dict_periods['Итоговые оценки']
        response2 = requests.get(
            url=f'https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId={perid}&subjectId=00000000-0000-0000-0000-000000000000&studentId={stid}',
            cookies=response_for_cook)
        soup = BeautifulSoup(response2.text, 'lxml')
        dict_lessons = json.loads(soup.text)  # Преобразовал str в dict
        find_lessons = dict_lessons['yearGradesTable']
        find_lessons2 = find_lessons['lessonGrades']  # --- (type - list)
        for i in find_lessons2:
            lesson_info = i['lesson']
            lesson_name = lesson_info['name']

            itog_ocenki_1 += f'{lesson_name}:\n'
            itog_ocenki_2 += f'{lesson_name}:\n'

            lesson_grades = i['grades']
            for x in lesson_grades:
                perid_1 = self.dict_periods['1 Полугодие']
                perid_2 = self.dict_periods['2 Полугодие']
                if perid_1 == x['periodId']:
                    sr_grade_1 = x['avarageGrade']
                    final_grade_1 = x['finallygrade']
                    itog_ocenki_1 += f'Средняя оценка: {sr_grade_1}\nИтоговая оценка: {final_grade_1}\n\n'
                elif perid_2 == x['periodId']:
                    sr_grade_2 = x['avarageGrade']
                    final_grade_2 = x['finallygrade']
                    itog_ocenki_2 += f'Средняя оценка: {sr_grade_2}\nИтоговая оценка: {final_grade_2}\n\n'
        print(itog_ocenki_1)
        print(itog_ocenki_2)
        return itog_ocenki_1, itog_ocenki_2

    def all_ocenki_pervoe_polygodie(self):
        """

        Передает все оценки(за первое полугодие) в виде:\n
        Предмет: оценка, оценка и т.д.

        """
        perid = self.dict_periods['1 Полугодие']
        response2 = requests.get(
            url=f'https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId={perid}&subjectId=00000000-0000-0000-0000-000000000000&studentId={stid}',
            cookies=response_for_cook)

        soup = BeautifulSoup(response2.text, 'lxml')
        dict_lessons = json.loads(soup.text)  # Преобразовал str в dict
        find_lessons = dict_lessons['periodGradesTable']
        find_lessons2 = find_lessons['disciplines']  # --- (type - list)
        itog = 'Все оценки:\n'

        for i in find_lessons2:
            grade = i['grades']
            lessson = i['name']
            itog += f'{lessson}: '
            for x in grade:
                if x['grades'] == []:
                    continue
                else:
                    ocenka = x['grades']
                    itog += f'{ocenka}, '
            itog += '\n'
        itog2 = re.sub('\[', '', itog)
        itog2 = re.sub('\]', '', itog2)
        itog2 = re.sub('\'', '', itog2)
        """
        как нибудь надо заменить
        на тоже что и в функции this_week
        """
        print(itog2)
        return itog2

    def this_week(self):
        """
        Получаем оценки за текущую неделю
        """
        perid = self.dict_periods['Текущая неделя']
        week = ''
        response = requests.get(url=f'https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId={perid}&subjectId=00000000-0000-0000-0000-000000000000&studentId={stid}',
                                cookies=response_for_cook)
        soup = BeautifulSoup(response.text, 'lxml')
        dict_week = json.loads(soup.text)
        search_grades = dict_week['weekGradesTable']
        search_grades2 = search_grades['days']
        for i in search_grades2:
            date = i['date']
            lessons = i['lessonGrades']
            date = time.strptime(date[0:10], '%Y-%m-%d')
            date = (f'{date.tm_mday}.{date.tm_mon}.{date.tm_year}')
            for name_and_grade in lessons:
                lesson = name_and_grade['name']
                number_of_lesson = name_and_grade['sequenceNumber']
                grades = name_and_grade['grades']
                for y in grades:
                    for ocenka in y:
                        week += f'Урок: {lesson}\nДата: {date}\nНомер урока: {number_of_lesson}\nОценка: {ocenka}\n\n'
        print(f'Все оценки за неделю.\n\n{week}')
        return week

    def select_variant(self):
        """
        Выберает вариант что спарсить\n
        По умолчанию стоит: Текущая неделя
        """
        if self.variant == 'Текущая неделя':
            ais.this_week()
        elif self.variant == '1 Полугодие':
            ais.all_ocenki_pervoe_polygodie()
        elif self.variant == '2 Полугодие':
            pass
        elif self.variant == 'Итоговые оценки':
            ais.find_itog_ocenki()


if __name__ == '__main__':
    ais = ais_dnevnik("DIzmestjev5f43", 't9vMzoB&Tw', 'Итоговые оценки')
    response_for_cook = ais.get_cook()  # -------- РАБОТАЕТ (получаем куки)
    stid = ais.search_all_id(response_for_cook)
    ais.select_variant()

"""

Еще надо будет все print в конце функций заменить на return
print -> return

"""
