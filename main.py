import pprint
import requests


def main():
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'User-Agent': 'MyApp/0.1b'
    }
    params = {
        'text': 'Программист',
        'area': 1,
        'period': 30
    }
    response = requests.get(url=url, headers=headers, params=params)
    pprint.pprint(response.json(), sort_dicts=False)


if __name__ == '__main__':
    main()