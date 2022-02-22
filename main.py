import requests


def main():
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'User-Agent': 'MyApp/0.1b'
    }
    params = {
        'text': 'Программист Python',
        'area': 1,
        'period': 30
    }
    response = requests.get(url=url, headers=headers, params=params)
    vacancies = response.json()
    salaries = []
    for vacancy in vacancies['items']:
        salaries.append(vacancy['salary'])
    print(*salaries, sep='\n')


if __name__ == '__main__':
    main()
