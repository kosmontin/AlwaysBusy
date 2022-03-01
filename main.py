import requests
from pprint import pprint
from tqdm import tqdm


def get_vacancy_summaries(lang):
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'User-Agent': 'MyApp/0.1b'
    }
    params = {
        'text': f'Программист {lang}',
        'area': 1,
        'period': 30
    }
    response = requests.get(url=url, headers=headers, params=params)
    response.raise_for_status()
    vacancies_page = response.json()
    was_found = vacancies_page['found']
    pages_number = vacancies_page['pages']
    has_salary = 0
    sum_salaries = 0
    vacancies = []
    for page in tqdm(range(pages_number)):
        for vacancy in vacancies_page['items']:
            avg_salary = predict_rub_salary(vacancy['salary'])
            vacancies.append({
                'id': vacancy['id'],
                'average_salary': avg_salary
            })
            if avg_salary:
                has_salary += 1
                sum_salaries += avg_salary
        params.update({'page': page})
        response = requests.get(url=url, headers=headers, params=params)
        response.raise_for_status()
        vacancies_page = response.json()
    summary = {
        lang: {
            'vacancies_found': was_found,
            'vacancies_processed': has_salary,
            'average_salary': int(sum_salaries / has_salary)
        }
    }
    return summary


def predict_rub_salary(salary):
    if salary and salary['currency'] == 'RUR' and (salary['from'] or salary['to']):
        if salary['from'] and salary['to']:
            return (int(salary['from']) + int(salary['to'])) / 2
        elif salary['from']:
            return int(salary['from']) * 1.2
        else:
            return int(salary['to']) * 0.8


def get_hh_vacancies():
    popular_languages = ['Python', 'Java', 'JavaScript', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']
    langs_summary = dict()
    for lang in popular_languages:
        print(lang)
        langs_summary.update(get_vacancy_summaries(lang))
    return langs_summary


def main():
    pass


if __name__ == '__main__':
    main()
