import page_analyzer as myapp
import os
import datetime
import pytest
import page_analyzer.db_utils
import collections
from fake_db_utils import FakePool


tests_path = os.path.dirname(__file__)


def get_html(filename):
    filepath = f'{tests_path}/fixtures/{filename}.html'
    with open(filepath) as f:
        file_data = f.read()
    return file_data


def test_html_parser_functions():
    right = get_html('right')
    data = myapp.get_parsed_data(right)
    assert data == {
        'h1': 'Test header',
        'title': 'Right',
        'description': 'Test content'
    }
    wrong = get_html('wrong')
    data = myapp.get_parsed_data(wrong)
    assert data == {
        'h1': '',
        'title': '',
        'description': ''
    }


def test_index(client):
    responce = client.get('/')
    assert bytes(
        '<title>Анализатор страниц</title>', 'utf-8'
    ) in responce.data
    assert bytes(
        '<body class="min-vh-100 d-flex flex-column">', 'utf-8'
    ) in responce.data
    assert bytes(
        '<a href="https://ru.hexlet.io/">Hexlet</a>', 'utf-8'
    ) in responce.data
    assert responce.status_code == 200


testdata = [
    (
        '',
        '/',
        bytes('<title>Анализатор страниц</title>', 'utf-8'),
        200
    ),
    (
        [{
            'id': 7,
            'name': 'https://itecnote.com',
            'created_at': datetime.datetime(2023, 9, 17, 18, 51, 23, 728078),
            'status_code': 200
        }],
        '/urls',
        bytes('<a href="/urls/7">https://itecnote.com</a>', 'utf-8'),
        200
    ),
    (
        [{
            'id': 1,
            'name': 'http://google.com',
            'url_id': 1,
            'status_code': 200,
            'h1': '',
            'title': 'Google',
            'description': 'Поиск информации в интернете',
            'created_at': datetime.datetime(2023, 9, 10, 18, 38, 14, 573159)
        }],
        '/urls/1',
        bytes('Поиск информации в интернете', 'utf-8'),
        200
    ),
    (
        '',
        '/page_not_found',
        bytes('Здесь нет', 'utf-8'),
        404
    )
]


@pytest.mark.parametrize("query, url, expected, status_code", testdata)
def test_get_handlers(client, query, url, expected, status_code):
    page_analyzer.db_utils.pool = FakePool(query)
    responce = client.get(url)
    assert expected in responce.data
    assert status_code == responce.status_code


testdata = [
    (
        'wrong url',
        bytes('Некорректный URL', 'utf-8'),
        422
    ),
    (
        f'http://{"very"*70}longurl.ru',
        bytes('URL превышает 255 символов', 'utf-8'),
        422
    ),
    (
        'Another bad url',
        bytes('<div class="alert alert-danger" role="alert">', 'utf-8'),
        422
    ),
    (
        'http://hexlet.io',
        bytes('Redirecting', 'utf-8'),
        302
    )
]


@pytest.mark.parametrize("input, expected, status_code", testdata)
def test_post_urls(client, input, expected, status_code):
    test_responce = collections.namedtuple('Test', ['count', 'id'])
    test_responce.count = 1
    test_responce.id = 1
    page_analyzer.db_utils.pool = FakePool(test_responce)

    responce = client.post(
        '/urls', data={'url': input}
    )
    assert expected in responce.data
    assert status_code == responce.status_code


def test_post_urls_id_checks(client):
    test_responce = collections.namedtuple('Test', ['name', 'id'])
    test_responce.name = 'http://hexlet.io'
    test_responce.id = '1'
    page_analyzer.db_utils.pool = FakePool(test_responce)
    responce = client.post('/urls/1/checks', data={'url': 'http://hexlet.io'})
    print(responce.text)
    assert responce.status_code == 302
