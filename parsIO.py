import asyncio
import json
import sqlite3
import locale

from datetime import datetime
from aiohttp import ClientSession

from dannie import PASSWORD, LOGIN

AUTH_LINK = 'https://dnevnik.egov66.ru/api/auth/Auth/Login'
STDID_LINK = 'https://dnevnik.egov66.ru/api/students'
ESTIMATE = 'https://dnevnik.egov66.ru/api/estimate'
API = 'https://dnevnik.egov66.ru/api/'


class AISdnevnik:
    def __init__(self, log: str = '', passw: str = '', **kwargs) -> None:
        self.login = log
        self.password = passw
        self.dict_periods: dict = {}
        self.periods: dict = {}
        self.periods_names: list = []
        self.status: int = 0
        self.class_id = ''
        self.stid = 0
        self.cook = ''
        self.year = ''
        self.dict_subjects = {}
        self.parent = False
        self.check = False

    async def check_acc(self) -> bool:
        data = json.dumps(
           {"login": f"{self.login}",
            "password": f"{self.password}"}
            )
        headers = {'Content-type': 'application/json',
                   'Content-Length': str(len(data)),
                   'charset': 'utf-8',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/000000000 Safari/537.36 OPR/000000000 (Edition Yx GX)'}

        async with ClientSession() as session:
            ses = await session.post(AUTH_LINK, data=data, headers=headers)
            status = ses.status
            if status == 200:
                self.status = 200
                cook: dict = await ses.json()
                for i in cook.items():
                    if i[0] == 'accessToken':
                        self.cook = i[1]
                await session.close()
                return True
            else:
                # print('ne norm')
                # print(self.login, self.password)
                self.status = status
                await session.close()
                return False

    async def check_cook(self) -> bool:
        # Если будут ошибки поменять все функции на get_info()
        if self.check is False:
            await self.get_info()
            self.check = True
            return True
        else:
            headers = {'Authorization': f'Bearer {self.cook}'}
            async with ClientSession() as session:
                x = await session.get(STDID_LINK, headers=headers)
                if x.status != 200:
                    await self.check_acc()
                    new_headers = {'Authorization': f'Bearer {self.cook}'}
                    x = await session.get(STDID_LINK, headers=new_headers)
                    if x.status == 200:
                        return True
                    else:
                        return False

    async def get_info(self) -> bool:
        if await self.check_acc():
            headers = {'Authorization': f'Bearer {self.cook}'}
            async with ClientSession() as session:

                id_search = await session.get(STDID_LINK, headers=headers)
                responce = await id_search.json()
                self.parent = responce['isParent']
                self.stid = responce['students'][0]['id']

                year_search = await session.get(f'{ESTIMATE}/years?studentId={self.stid}', headers=headers)
                years = await year_search.json()
                self.year = years['currentYear']['id']

                class_id = await session.get(f'{API}classes?studentId={self.stid}&schoolYear={self.year}', headers=headers)
                clas = await class_id.json()
                self.class_id = clas['currentClass']['value']

                periods = await session.get(f'{ESTIMATE}/periods?schoolYear={self.year}&classId={self.class_id}&studentId={self.stid}', headers=headers)
                period = await periods.json()
                for i in period['periods']:
                    self.periods_names.append(i['name'])
                    self.dict_periods[i['name']] = i['id']
                    self.periods[i['id']] = i['name']
                return True
        else:
            pass

    async def select_var(self, period, **kwargs) -> str | tuple[str, bool, bool, int]:
        if await self.check_cook():

            headers = {'Authorization': f'Bearer {self.cook}'}
            period_id = self.dict_periods[period]

            async with ClientSession() as session:

                if 'page' in kwargs:
                    page = kwargs['page']
                    subjects = await session.get(f'{ESTIMATE}?schoolYear={self.year}&classId={self.class_id}&periodId={period_id}&subjectId=00000000-0000-0000-0000-000000000000&studentId={self.stid}&weekNumber={page}', headers=headers)
                    grades: dict = await subjects.json()
                else:
                    page = None
                    subjects = await session.get(f'{ESTIMATE}?schoolYear={self.year}&classId={self.class_id}&periodId={period_id}&subjectId=00000000-0000-0000-0000-000000000000&studentId={self.stid}', headers=headers)
                    grades: dict = await subjects.json()

                if grades['yearGradesTable'] is not None:
                    lessons = grades['yearGradesTable']['lessonGrades']
                    mes = ''

                    for lesson in lessons:
                        name = lesson['lesson']['name']
                        year_grade = lesson['yearGrade']
                        if year_grade is None:
                            year_grade = '-'
                        test_grade = lesson['testGrade']
                        if test_grade is None:
                            test_grade = '-'
                        finaly_grade = lesson['finalyGrade']
                        if finaly_grade is None:
                            finaly_grade = '-'

                        mes += f'📎{name}\nОценки:\nГод:{year_grade} Экзамен:{test_grade} Итог:{finaly_grade}\n'

                        for grade in lesson['grades']:
                            if grade['periodId'] in self.periods:
                                quater_grade_pr = grade['averageGrade']
                                quater_grade_pr = round(quater_grade_pr, 2)
                                quater_grade = grade['finallygrade']
                                if quater_grade is None:
                                    quater_grade = '0'
                                quater = self.periods[grade['periodId']]
                                mes += f'{quater}:\nСр.Оценка: {quater_grade_pr} Итог: {quater_grade}\n'
                        mes += '\n'
                    return mes

                else:
                    if grades['periodGradesTable'] is not None:
                        mes = f'Оценки за {period}:\n\n'
                        presence_N = 0
                        presence_good = 0
                        presence_bol = 0
                        presence_all = 0
                        disciplines = grades['periodGradesTable']['disciplines']

                        for discipline in disciplines:

                            name = discipline['name']
                            mes += f'📎Предмет: {name}\n'

                            average_Grade = discipline['averageGrade']
                            if average_Grade is None:
                                average_Grade = 0
                            else:
                                average_Grade = round(average_Grade, 2)
                            mes += f'Ср.оценка: {average_Grade}\n'

                            total_Grade = discipline['totalGrade']
                            if total_Grade is None:
                                total_Grade = 0
                            mes += f'Итоговая оценка: {total_Grade}\n'

                            mes += 'Все оценки: '
                            for grade_inf in discipline['grades']:

                                if grade_inf['grades'] != []:
                                    last_grade = grade_inf['grades'][0]
                                    for grade in last_grade:
                                        mes += f'{grade}, '

                                if grade_inf['presence'] is not None:
                                    presence = grade_inf['presence']
                                    if presence == 'Н':
                                        presence_N += 1
                                    elif presence == 'У':
                                        presence_good += 1
                                    elif presence == 'Б':
                                        presence_bol += 1
                                    mes += f'{presence}, '
                            mes += '\n\n'
                        presence_all += presence_good + presence_N + presence_bol

                        mes += 'Пропуски:\n'
                        mes += f'Всего пропусков: {presence_all}\n'
                        mes += f'По Ув.причине: {presence_good}\n'
                        mes += f'По не Ув.причине: {presence_N}\n'
                        mes += f'По болезни: {presence_bol}\n'
                        return mes

                    else:
                        if grades['weekGradesTable'] is not None:
                            locale.setlocale(locale.LC_ALL, 'ru_RU')

                            week_start = grades['weekGradesTable']['beginDate']
                            start_obj = datetime.fromisoformat(week_start)
                            start = start_obj.strftime("%d %B")

                            week_end = grades['weekGradesTable']['endDate']
                            end_obj = datetime.fromisoformat(week_end)
                            end = end_obj.strftime("%d %B")

                            pagination = grades['weekGradesTable']['paginationData']
                            page = pagination['pageNumber']
                            next_page: bool = pagination['hasNextPage']
                            previous_page: bool = pagination['hasPreviousPage']

                            mes = f'{page}-ая неделя: {start} - {end}\n'

                            if grades['weekGradesTable']['days'] == []:
                                mes += 'На этой неделе оценок нет.'
                                return mes, next_page, previous_page, page
                            else:
                                for day in grades['weekGradesTable']['days']:
                                    date_str = day['date']
                                    dt_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")

                                    day_of_week = dt_obj.strftime("%A")
                                    date_str_formatted = f"{day_of_week} {dt_obj.day}.{dt_obj.month:02d}"
                                    mes += f'📎{date_str_formatted}\n'

                                    for lesson in day['lessonGrades']:

                                        lesson_name = lesson['name']
                                        sequence = lesson['sequenceNumber']
                                        mes += f'🗓{sequence} урок: {lesson_name} '

                                        if lesson['beginHour'] is not None:
                                            start_h = lesson['beginHour']
                                            mes += f'{start_h}:'
                                        if lesson['beginMinute'] is not None:
                                            start_m = lesson['beginMinute']
                                            if start_m == 0:
                                                start_m = '00'
                                            mes += f'{start_m} - '
                                        if lesson['endHour'] is not None:
                                            end_h = lesson['endHour']
                                            mes += f'{end_h}:'
                                        if lesson['endMinute'] is not None:
                                            end_m = lesson['endMinute']
                                            mes += f'{end_m}\n'
                                        else:
                                            mes += '\n'

                                        grade_day = lesson['grades']
                                        mes += 'Оценки: '

                                        for grade in grade_day:
                                            mes += f'{grade[0]} '
                                        mes += '\n\n'
                                    mes += '\n'
                            return mes, next_page, previous_page, page

    async def return_periods(self) -> dict:
        if await self.get_info():
            return self.dict_periods

    async def accs_info(self) -> str:
        if await self.check_cook():
            headers = {'Authorization': f'Bearer {self.cook}'}

            async with ClientSession() as session:

                student = await session.get(STDID_LINK, headers=headers)
                info = await student.json()
                if info['isParent'] is False:
                    stud_inf = info['students']
                    first_name = stud_inf[0]['firstName']
                    lastName = stud_inf[0]['lastName']
                    mes = f'{first_name} {lastName}'
                    return mes

    async def return_main_login(user_id) -> list:
        ids = []
        connection = sqlite3.connect('accs.db')
        cursor = connection.cursor()
        cursor.execute('SELECT user_id FROM Users')
        results = cursor.fetchall()
        for i in results:
            ids.append(i[0])
        return ids


async def main():
    x = await AISdnevnik(log=LOGIN, passw=PASSWORD).select_var('Текущая неделя', page=35)
    for i in x:
        print(i)
    # print(await AISdnevnik().return_main_login())


if __name__ == '__main__':
    asyncio.run(main())
