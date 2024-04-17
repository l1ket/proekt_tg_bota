import asyncio
import json
import inspect

from aiohttp import ClientSession

AUTH_LINK = 'https://dnevnik.egov66.ru/api/auth/Auth/Login'
STDID_LINK = 'https://dnevnik.egov66.ru/api/students'
ESTIMATE = 'https://dnevnik.egov66.ru/api/estimate/'
API = 'https://dnevnik.egov66.ru/api/'


class AISdnevnik:
    def __init__(self, log: str = '', passw: str = '', variant: str = 'Текущая неделя', **period: dict) -> None:
        self.login = log
        self.password = passw
        self.variant = variant
        self.dict_periods: dict = period
        self.periods_names: list = []
        self.status: int = 0
        self.class_id = ''
        self.stid = 0
        self.cook = ''
        self.year = ''
        self.dict_subjects = {}
        self.parent = False

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
                print('ne norm')
                print(self.login, self.password)
                self.status = status
                await session.close()
                return False

    async def get_info(self) -> bool:
        if await self.check_acc():
            headers = {'Authorization': f'Bearer {self.cook}'}
            async with ClientSession() as session:

                id_search = await session.get(STDID_LINK, headers=headers)
                responce = await id_search.json()
                self.parent = responce['isParent']
                self.stid = responce['students'][0]['id']

                year_search = await session.get(f'{ESTIMATE}years?studentId={self.stid}', headers=headers)
                years = await year_search.json()
                self.year = years['currentYear']['id']

                class_id = await session.get(f'{API}classes?studentId={self.stid}&schoolYear={self.year}', headers=headers)
                clas = await class_id.json()
                self.class_id = clas['currentClass']['value']

                periods = await session.get(f'{ESTIMATE}periods?schoolYear={self.year}&classId={self.class_id}&studentId={self.stid}', headers=headers)
                period = await periods.json()
                for i in period['periods']:
                    self.periods_names.append(i['name'])
                    self.dict_periods[i['name']] = i['id']
                
                return True
        else:
            pass

    async def week_grades(self) -> None:
        if await self.get_info():
            headers = {'Authorization': f'Bearer {self.cook}'}
            async with ClientSession() as session:
                period_id = self.dict_periods[self.periods_names[0]]
                week_grades = await session.get(
                    f'{API}estimate?schoolYear={self.year}&classId={self.class_id}&periodId={period_id}&subjectId=00000000-0000-0000-0000-000000000000&studentId={self.stid}', headers=headers)
                week_grades = await week_grades.json()
                curent_week = week_grades['weekGradesTable']
                print(week_grades)
                return
        else:
            pass


async def main():
    await AISdnevnik('DIzmestjev5f43', 't9vMzoB&Tw').week_grades()


if __name__ == '__main__':
    asyncio.run(main())
