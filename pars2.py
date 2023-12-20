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
import datetime


class ais_dnevnik:
    """
    Класс аис дневник.
    самый важный все что написано в self
    сделанно специально для начальной и последующей
    инициализации нужных данных
    """
    def __init__(self, log='', passw='', variant='Текущая неделя', **period) -> None:
        self.login = log
        self.password = passw
        self.variant = variant
        self.dict_periods = period
        self.status = 0
        self.stid = 0
        self.response_for_cook = ''
        self.dict_subjects = {}

    def get_status(self):
        """
        Получаем статус для тг бота
        (есть интресная ситуация - на сайте есть аккаунт
        с учетными данными: 123 123
        и получается что на этот акк можно зайти,
        но он не юзабельный)
        """

        if self.login == 123 or self.login == '123' and self.password == 123 or self.password == '123':
            return 0

        link = 'https://dnevnik.egov66.ru/api/auth/Auth/Login'  # Пока хост не сменят ссылка не меняется(хост сменили в этот ноябрь, так что могут еще раз, хотя хост уже только на нашу область так что врятли)
        data = json.dumps({"login": f"{self.login}",
                        "password": f"{self.password}"})

        headers = {'Content-type': 'application/json',
                    'Content-Length': str(len(data)),
                    'charset': 'utf-8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0 (Edition Yx GX)'}

        response_for_cook = requests.post(link, data=data,
                                        headers=headers).status_code  # Проверка подошли данные или нет
        # print(response_for_cook)
        if response_for_cook == 200:
            self.status = 200
        else:
            print('ne norm')
            print(self.login, self.password)
            self.status == response_for_cook
        return self.status

    def get_cook(self):
        """
        Лутаем куки.
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
            self.response_for_cook = requests.post(link, data=data,
                                        headers=headers).cookies
            return self.response_for_cook
        else:
            print('ne norm')
            print(self.login, self.password)
            self.status == response_for_cook
            return self.status

    def search_all_id(self):
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

        response_for_url = requests.get(url='https://dnevnik.egov66.ru/api/students', cookies=self.response_for_cook).text
        response_for_url_str = json.loads(response_for_url)
        response_for_url_str = response_for_url_str['students']

        for stid in response_for_url_str:
            self.stid = stid['id']

        response_for_period = requests.get(url=f'https://dnevnik.egov66.ru/api/estimate/periods?schoolYear=2023&studentId={self.stid}', cookies=self.response_for_cook).text
        response_for_period_str = json.loads(response_for_period)
        response_for_period_str = response_for_period_str['periods']

        for i in response_for_period_str:
            name_period = i['name']
            id_period = i['id']
            self.dict_periods[name_period] = id_period

        return self.stid

    def find_itog_ocenki(self):  # С 9-11 классы
        """
        Получаем буквально все оценки из вкладки 'Итоговые оценки'\n
        Кроме оценок за экзамен и похожих(потому что не целесообразно)
        Вообщем в ссылке нужно 4 элемента(хотя мб нет, получается и без них):\n
        schoolYear = нет(его либо нельзя найти либо я плохо искал,
        так что будем сами ставить года)\n
        periodId = есть\n
        subjectId = нет
        (используется в случае если перейти во вкладку отдельного предмета)\n
        studentId = есть\n
        (самая долгая функция в плане ожидания по времени)
        """

        itog_ocenki_1 = 'Итоговые оценки за 1 полугодие(если стоит None или 0, то учителя еще не выставили):\n\n'
        itog_ocenki_2 = 'Итоговые оценки за 2 полугодие(если стоит None или 0, то учителя еще не выставили):\n\n'
        perid = self.dict_periods['Итоговые оценки']
        response2 = requests.get(
            url=f'https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId={perid}&subjectId=00000000-0000-0000-0000-000000000000&studentId={self.stid}',
            cookies=self.response_for_cook)
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

        itog_ocenki = f'{itog_ocenki_1}\n{itog_ocenki_2}'
        return itog_ocenki

    def find_itog_ocenki_nine(self):  # С 1-9 классы

        itog_ocenki = ''
        itog_ocenki_1 = 'Первая четверть:\n\n'
        itog_ocenki_2 = 'Вторая четверть:\n\n'
        itog_ocenki_3 = 'Третья четверть:\n\n'
        itog_ocenki_4 = 'Четвёртая четверть:\n\n'

        perid = self.dict_periods['Итоговые оценки']
        response2 = requests.get(
            url=f'https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId={perid}&subjectId=00000000-0000-0000-0000-000000000000&studentId={self.stid}',
            cookies=self.response_for_cook)
        soup = BeautifulSoup(response2.text, 'lxml')
        dict_lessons = json.loads(soup.text)  # Преобразовал str в dict
        find_lessons = dict_lessons['yearGradesTable']
        find_lessons2 = find_lessons['lessonGrades']  # --- (type - list)

        for i in find_lessons2:
            lesson_info = i['lesson']
            lesson_name = lesson_info['name']

            itog_ocenki_1 += f'{lesson_name}:\n'
            itog_ocenki_2 += f'{lesson_name}:\n'
            itog_ocenki_3 += f'{lesson_name}:\n'
            itog_ocenki_4 += f'{lesson_name}:\n'

            lesson_grades = i['grades']
            for x in lesson_grades:

                perid_1 = self.dict_periods['1 Четверть']
                perid_2 = self.dict_periods['2 Четверть']
                perid_3 = self.dict_periods['3 Четверть']
                perid_4 = self.dict_periods['4 Четверть']

                if perid_1 == x['periodId']:

                    sr_grade_1 = x['avarageGrade']
                    final_grade_1 = x['finallygrade']
                    itog_ocenki_1 += f'Средняя оценка: {sr_grade_1}\nИтоговая оценка: {final_grade_1}\n\n'

                elif perid_2 == x['periodId']:

                    sr_grade_2 = x['avarageGrade']
                    final_grade_2 = x['finallygrade']
                    itog_ocenki_2 += f'Средняя оценка: {sr_grade_2}\nИтоговая оценка: {final_grade_2}\n\n'

                elif perid_3 == x['periodId']:

                    sr_grade_1 = x['avarageGrade']
                    final_grade_1 = x['finallygrade']
                    itog_ocenki_3 += f'Средняя оценка: {sr_grade_1}\nИтоговая оценка: {final_grade_1}\n\n'

                elif perid_4 == x['periodId']:

                    sr_grade_2 = x['avarageGrade']
                    final_grade_2 = x['finallygrade']
                    itog_ocenki_4 += f'Средняя оценка: {sr_grade_2}\nИтоговая оценка: {final_grade_2}\n\n'

        itog_ocenki += f'{itog_ocenki_1}\n{itog_ocenki_2}\n'
        itog_ocenki += f'{itog_ocenki_3}\n{itog_ocenki_4}'
        # print(itog_ocenki)

        return itog_ocenki

    def all_ocenki_pervoe_polygodie(self):
        """
        Передает все оценки(за первое полугодие) в виде:\n
        Предмет: оценка, оценка и т.д.
        """

        perid = self.dict_periods['1 Полугодие']
        response2 = requests.get(
            url=f'https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId={perid}&subjectId=00000000-0000-0000-0000-000000000000&studentId={self.stid}',
            cookies=self.response_for_cook)

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

        return itog2

    def this_week(self):
        """
        Получаем оценки за текущую неделю
        """

        perid = self.dict_periods['Текущая неделя']
        week = ''
        response = requests.get(url=f'https://dnevnik.egov66.ru/api/estimate?schoolYear=2023&periodId={perid}&subjectId=00000000-0000-0000-0000-000000000000&studentId={self.stid}',
                                cookies=self.response_for_cook)
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
        this_week = f'Все оценки за неделю (если пусто значит на неделе оценок нет).\n\n{week}'
        return this_week

    def all_subjects(self):

        counter = 0
        subjects = ''
        response = requests.get(url=f'https://dnevnik.egov66.ru/api/estimate/subjects?schoolYear=2023&studentId={self.stid}',
                                cookies=self.response_for_cook)
        soup = BeautifulSoup(response.text, 'lxml')
        dict_week = json.loads(soup.text)
        list_subjects = dict_week['subjects']
        list_len = len(list_subjects)
        for i in list_subjects[:list_len-1]:
            counter += 1
            name = i['name']
            subjects += f'{counter}. {name}\n'
            id_subject = i['id']
            self.dict_subjects[f'{name}'] = f'{id_subject}'
        return subjects

    def current_subject(self, subject):
        """
        Получаем оценки по конкретному предмету
        """

        if subject not in self.dict_subjects:
            text = 'В списке нет такого предмета. :('
            print(text)
            return text
        else:
            les_id = self.dict_subjects[f'{subject}']
            print(les_id)
            week = ''
            response = requests.get(url=f'https://dnevnik.egov66.ru/api/lesson/allGrades?lessonId={les_id}&studentId={self.stid}',
                                    cookies=self.response_for_cook)
            soup = BeautifulSoup(response.text, 'lxml')
            print(soup)
            dict_week = json.loads(soup.text)
            print(dict_week)
            """
            Супер тяжелые данные, пока что скип.
            возможно генерируются случайно.
            """
        ...

    def homework_this_day(self):

        home_works = ''
        date = datetime.datetime.now()
        date = date.date()
        # print(date)
        response = requests.get(url=f'https://dnevnik.egov66.ru/api/homework?date={date}&studentId={self.stid}',
                                cookies=self.response_for_cook)
        soup = BeautifulSoup(response.text, 'lxml')
        dict_week = json.loads(soup.text)
        home_work = dict_week['homeworks']
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
        home_works += f'Выбранный день: {date}/{day_week}\n'
        if day_week == 'Суббота' or day_week == 'Воскресенье':
            home_works += 'Это выходной.'
            print(home_works)
            return home_works
        else:
            home_works += 'Д/З(Если пусто то ничего не задали):\n\n'
            for i in home_work:
                counter = 0
                name_file = ''
                name = i['lessonName']
                description = i['description']
                files = i['homeWorkFiles']
                for x in files:
                    counter += 1
                    id_file = x['id']
                    name_file += x['name']
                    # response = requests.get(url=f'https://dnevnik.egov66.ru/api/lesson/homework/files/{id_file}',
                    #             cookies=self.response_for_cook)
                    # with open(f"tutorial{counter}.pdf", "wb") as code:
                    #     code.write(response.content)
                    # with open(f"tutorial{counter}.docx", "wb") as code:
                    #     code.write(response.content)
                    # # print(soup)
                    """
                    скачка файлов, работает только pdf
                    """
                home_works += f'Название урока: {name}\nОписание Д/З: {description}\n'
                home_works += f'Прикреплённые файлы: {name_file}\n\n'
                # /api/lesson/homework/files/37656041-e6c0-4f7d-bb09-d6e8cff8dbb9
        # print(home_works)
        return home_works

    def student_info(self):
        '''
        Данные об ученике или родителе
        '''

        response = requests.get(url=f'https://dnevnik.egov66.ru/api/students',
                                cookies=self.response_for_cook)
        soup = BeautifulSoup(response.text, 'lxml')
        page = json.loads(soup.text)
        parent = page['isParent']

        if parent is False:
            parent = 'Ученик'
        else:
            parent = 'Родитель'

        results = f'Роль: {parent}\n'
        info = page['students']

        for i in info:
            first_name = i['firstName']
            last_name = i['lastName']
            sur_name = i['surName']
            class_name = i['className']
            school = i['orgName']
            results += f'ФИО: {last_name} {first_name} {sur_name}\n'
            results += f'Класс: {class_name}\n'
            results += f'Школа: {school}'

        return results

    def select_variant(self):
        """
        Выберает вариант что спарсить\n
        По умолчанию стоит: Текущая неделя
        """

        if self.variant == 'Текущая неделя':
            this_week = ais_dnevnik.this_week(self)
            return this_week
        elif self.variant == '1 Полугодие':
            polygodie_1 = ais_dnevnik.all_ocenki_pervoe_polygodie(self)
            return polygodie_1
        elif self.variant == '2 Полугодие':
            pass
        elif self.variant == 'Итоговые оценки':
            itog = ais_dnevnik.find_itog_ocenki(self)
            return itog
        elif self.variant == 'Итоговые оценки_9':
            itog = ais_dnevnik.find_itog_ocenki_nine(self)
            return itog
        elif self.variant == 'Все предметы':
            sub = ais_dnevnik.all_subjects(self)
            return sub
        elif self.variant == 'Домашнее задание этот день':
            home = ais_dnevnik.homework_this_day(self)
            return home
        elif self.variant == 'Данные о аккаунте':
            home = ais_dnevnik.student_info(self)
            return home


if __name__ == '__main__':
    ais = ais_dnevnik("DIzmestjeva", '123456', 'Данные о аккаунте')
    response_for_cook = ais.get_cook()  # -------- РАБОТАЕТ (получаем куки)
    stid = ais.search_all_id()
    # ais.homework_this_day()
    ais.select_variant()
    # ais.all_subjects()
    # ais.current_subject('Химия')
