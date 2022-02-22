import requests


def main():
    popular_languages = ['Python', 'Java', 'JavaScript', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'User-Agent': 'MyApp/0.1b'
    }
    params = {
        'area': 1,
        'period': 30
    }
    vacancy_counters = dict()
    for lang in popular_languages:
        params.update({'text': f'Программист {lang}'})
        response = requests.get(url=url, headers=headers, params=params)
        vacancy_counters[lang] = response.json()['found']
    print(vacancy_counters)


if __name__ == '__main__':
    main()
