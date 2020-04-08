import requests
import time

import pprint


class HHResponseError(Exception):
    def __init__(self, message, errors):

        # Call the base class constructor with the parameters it needs
        super(HHResponseError, self).__init__(message)

        # Now for your custom code...
        self.errors = errors


class HH:

    API = 'https://api.hh.ru'
    VACANCY_METHOD = '/vacancies'
    AREA_METHOD = '/areas'

    @staticmethod
    def get_areas(area_search=None):
        url = f'{HH.API}{HH.AREA_METHOD}'
        result = requests.get(url)
        json_result = result.json()
        russia_result = [item['areas'] for item in json_result if item.get('name').lower() == 'Россия'.lower()]
        if area_search:
            area_result = [item for item in russia_result[0] if area_search.lower() in item.get('name').lower()]
        else:
            area_result = [item for item in russia_result[0]]
        return [{'id': item['id'], 'name': item['name']} for item in area_result]

    @staticmethod
    def get_key_skills(job_title, area=None):

        key_skills = {}
        vacancy_info = {}
        list_salary = []

        vacancies = HH.get_vacancies(job_title, area)
        i = 0
        vacancy_info['count'] = len(vacancies)

        for vacancy in vacancies:
            url = vacancy['api_url']
            result = requests.get(url)
            if result.status_code == 400:
                raise HHResponseError
            json_result = result.json()

            i += 1
            if i > 100:
                time.sleep(5)  # Если постоянносо дергать сервер то hh посылает далеко
                i = 0

            for skill_name in json_result['key_skills']:
                key_skills[skill_name['name']] = key_skills.get(skill_name['name'], 0) + 1

            salary = json_result['salary']
            if salary:
                gross = salary['gross']
                if salary['currency'].lower() == 'rur':
                    if 'from' in salary.keys():
                        if salary['from']:
                            list_salary.append(salary['from'] if gross else salary['from'] / 0.87)
                    if 'to' in salary.keys():
                        if salary['to']:
                            list_salary.append(salary['to'] if gross else salary['to'] / 0.87)

        vacancy_info['key_skills'] = key_skills
        vacancy_info['avg_salary'] = sum(list_salary) / len(list_salary)

        return vacancy_info

    @staticmethod
    def get_vacancies(job_title, area=None):

        def urls_from_json(jr):
            return [{'api_url': item['url']} for item in jr['items']]

        params = {'text': job_title}
        if not (area is None):
            params['area'] = area
        url = f'{HH.API}{HH.VACANCY_METHOD}'
        result = requests.get(url, params=params)
        if result.status_code == 400:
            raise HHResponseError
        json_result = result.json()
        pages = json_result['pages']
        return_urls = urls_from_json(json_result)
        if pages > 1:  # Если вернулось больше одной страницы
            for current_page in range(1, pages):
                params['page'] = current_page
                result = requests.get(url, params=params)
                json_result = result.json()
                return_urls = return_urls + urls_from_json(json_result)
        return return_urls