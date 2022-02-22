import requests


def predict_rub_salary(id):
    url = f'https://api.hh.ru/vacancies/{id}'
    headers = {
        'User-Agent': 'MyApp/0.1b'
    }
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    salary = response.json()['salary']
    if salary and salary['currency'] == 'RUR' and (salary['from'] or salary['to']):
        if salary['from'] and salary['to']:
            return (int(salary['from']) + int(salary['to'])) / 2
        elif salary['from']:
            return int(salary['from']) * 1.2
        else:
            return int(salary['to']) * 0.8


def main():
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'User-Agent': 'MyApp/0.1b'
    }
    json = {
        'text': 'Программист Python',
        'area': 1,
        'period': 30
    }
    response = requests.get(url=url, headers=headers, json=json)
    response.raise_for_status()
    vacancies = response.json()['items']
    for vacancy in vacancies:
        print(predict_rub_salary(vacancy['id']))


if __name__ == '__main__':
    main()
