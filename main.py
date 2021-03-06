import itertools
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
    vacancies = {'items': []}
    for page in itertools.count(1):
        response = requests.get(url=url, headers=headers, params=params)
        response.raise_for_status()
        vacancies_page = response.json()
        for vacancy in vacancies_page['items']:
            vacancies['items'].append({
                'id': vacancy['id'],
                'salary': predict_rub_salary(
                    vacancy['salary']['from'],
                    vacancy['salary']['to'],
                    vacancy['salary']['currency']) if vacancy['salary'] else None
            })
        if vacancies_page['pages'] == page:
            vacancies['found'] = vacancies_page['found']
            break
        else:
            params['page'] = page
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
    vacancies = {'items': []}
    for page in itertools.count(1):
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        vacancies_page = response.json()
        for vacancy in vacancies_page['objects']:
            vacancies['items'].append({
                'id': vacancy['id'],
                'salary': predict_rub_salary(
                    vacancy['payment_from'],
                    vacancy['payment_to'],
                    vacancy['currency'])
            })
        if vacancies_page['more']:
            params['page'] = page
        else:
            vacancies['found'] = vacancies_page['total']
            break
    return vacancies


def predict_rub_salary(salary_from, salary_to, currency):
    if currency in ('RUR', 'rub') and (salary_from or salary_to):
        if salary_from and salary_to:
            avg_salary = (int(salary_from) + int(salary_to)) / 2
        elif salary_from:
            avg_salary = int(salary_from) * 1.2
        else:
            avg_salary = int(salary_to) * 0.8
        return avg_salary


def get_summary_by_langs(vacancies_source, langs=POPULAR_LANGUAGES):
    summary = {}
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
    table_data = [['Язык программирования',
                   'Вакансий найдено',
                   'Вакансий обработано',
                   'Средняя зарплата']]
    for lang, values in data.items():
        table_data.append([lang,
                           values['vacancies_found'],
                           values['vacancies_processed'],
                           values['average_salary']])
    table = AsciiTable(table_data, source_name)
    print('\n', table.table)


if __name__ == '__main__':
    load_dotenv()
    print_pretty_table(get_summary_by_langs(get_sj_vacancies), 'SuperJob Moscow')
    print_pretty_table(get_summary_by_langs(get_hh_vacancies), 'HeadHunter Moscow')
