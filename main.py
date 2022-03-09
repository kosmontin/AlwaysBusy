import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable
from tqdm import tqdm

POPULAR_LANGUAGES = ('Python', 'Java', 'JavaScript', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go')


def get_hh_vacancies(lang='Python', area=1, period=30):
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'User-Agent': 'MyApp/0.1b'
    }
    params = {
        'text': f'Программист {lang}',
        'area': area,
        'period': period
    }
    response = requests.get(url=url, headers=headers, params=params)
    response.raise_for_status()
    vacancies_page = response.json()
    pages = vacancies_page['pages']
    found = vacancies_page['found']
    vacancies = {'items': []}
    for page in range(pages):
        for vacancy in vacancies_page['items']:
            vacancies['items'].append({
                'id': vacancy['id'],
                'salary': predict_rub_salary({
                    'from': vacancy['salary']['from'],
                    'to': vacancy['salary']['to'],
                    'currency': vacancy['salary']['currency']
                }) if vacancy['salary'] else None
            })
        params.update({'page': page})
        response = requests.get(url=url, headers=headers, params=params)
        response.raise_for_status()
        vacancies_page = response.json()
    vacancies['found'] = found
    return vacancies


def get_sj_vacancies(lang='Python'):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': os.getenv('SJ_API_KEY')
    }
    params = {
        'town': 'Москва',
        'keyword': f'Программист {lang}',
        'catalogues': 48
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    vacancies_page = response.json()
    vacancies = {'items': []}
    found = vacancies_page['total']
    page = 0
    more = True
    while more:
        for vacancy in vacancies_page['objects']:
            vacancies['items'].append({
                'id': vacancy['id'],
                'salary': predict_rub_salary({
                    'from': vacancy['payment_from'],
                    'to': vacancy['payment_to'],
                    'currency': vacancy['currency']
                })
            })
        page += 1
        more = vacancies_page['more']
        params.update({'page': page})
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        vacancies_page = response.json()
    vacancies['found'] = found
    return vacancies


def predict_rub_salary(salary):
    if salary and salary['currency'] in ('RUR', 'rub') and (salary['from'] or salary['to']):
        if salary['from'] and salary['to']:
            return (int(salary['from']) + int(salary['to'])) / 2
        elif salary['from']:
            return int(salary['from']) * 1.2
        else:
            return int(salary['to']) * 0.8


def get_summary_by_langs(vacancies_source, langs=POPULAR_LANGUAGES):
    summary = dict()
    for lang in tqdm(langs, desc='Processing of popular languages: '):
        vacancies = vacancies_source(lang)
        salaries = []
        for vacancy in vacancies['items']:
            if vacancy['salary']:
                salaries.append(vacancy['salary'])
        summary[lang] = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': len(salaries),
            'average_salary': int(sum(salaries) / len(salaries)) if salaries else 0
        }
    return summary


def print_pretty_table(data, source_name=None):
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for lang, values in data.items():
        table_data.append([lang, values['vacancies_found'], values['vacancies_processed'], values['average_salary']])
    table = AsciiTable(table_data, source_name)
    print('\n', table.table)


if __name__ == '__main__':
    load_dotenv()
    print_pretty_table(get_summary_by_langs(get_sj_vacancies), 'SuperJob Moscow')
    print_pretty_table(get_summary_by_langs(get_hh_vacancies), 'HeadHunter Moscow')
