from hh import HH
import json


import pprint

ans = ''
while not (ans == '0'):
    print('Поиск информации по вакансиям')
    print('1 - поиск по наименованию вакансии')
    print('2 - просмотреть список регионов и кодов')
    print('3 - просмотреть самые востребованные навыки')
    print('0 - завершить программу')

    ans = input('Введите пункт меню: ')
    if ans == '2':
        region_text = input('Введите часть названия региона (или оставте пустым):')
        regions = HH.get_areas(region_text) if region_text != '' else HH.get_areas()
        for region in sorted(regions, key=lambda x: int(x['id'])):
            print('Код:', region['id'], region['name'])
        print()

    if ans == '1':
        vacancy_text = input('Введите часть название вакансии: ')
        region_code = input('Введите код региона (или пусто): ')
        if region_code == '':
            vacancy_result = HH.get_key_skills(vacancy_text, None)
        else:
            vacancy_result = HH.get_key_skills(vacancy_text, region_code)

        with open('data.json', 'w') as fp:
            json.dump(vacancy_result, fp)

        pprint.pprint(vacancy_result)
        print()

    if ans == '3':
        with open('data.json', 'r') as fp:
            vacancy_result = json.load(fp)
            print('Количество найденных вакансий', vacancy_result['count'])
            print('Средняя зарплата (net)', '{:.2f}'.format(vacancy_result['avg_salary']))
            print('Ключевые навыки')
            key_skills = vacancy_result['key_skills']
            skills_sorted = sorted(key_skills.items(), key=lambda x: int(x[1]), reverse=True)
            i = 0
            for skill in skills_sorted:
                print(skill[0], skill[1])
                i += 1
                if i == 10:
                    break
        print()