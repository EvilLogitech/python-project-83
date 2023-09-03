import page_analyzer as myapp
import pytest
from bs4 import BeautifulSoup
import os


tests_path = os.path.dirname(__file__)


def test_html_parser_functions():
    right = get_html('right')
    assert myapp.get_h1(right) == 'Test header'
    assert myapp.get_title(right) == 'Right'
    assert myapp.get_description(right) == 'Test content'
    wrong = get_html('wrong')
    assert myapp.get_h1(wrong) == ''
    assert myapp.get_title(wrong) == ''
    assert myapp.get_description(wrong) == ''


def get_html(filename):
    filepath = f'{tests_path}/fixtures/{filename}.html'
    with open(filepath) as f:
        file_data = f.read()
    return BeautifulSoup(file_data, 'html.parser')


def test_templates(client):
    responce = client.get('/')
    assert bytes(
        '<title>Анализатор страниц</title>', 'utf-8'
    ) in responce.data
    assert bytes(
        '<a href="https://ru.hexlet.io/">Hexlet</a>', 'utf-8'
    ) in responce.data
    responce = client.get('/urls')
    assert bytes(
        '<th>Последняя проверка</th>', 'utf-8'
    ) in responce.data


testdata = [
    (
        'wrong url',
        bytes('Некорректный URL', 'utf-8')
    ),
    (
        f'http://{"very"*70}longurl.ru',
        bytes('URL превышает 255 символов', 'utf-8')
    ),
    (
        'Another bad url',
        bytes('<div class="alert alert-danger" role="alert">', 'utf-8')
    )
]


@pytest.mark.parametrize("input, expected", testdata)
def test_validator(client, input, expected):
    responce = client.post(
        '/urls', data={'url': input}
    )
    assert expected in responce.data


def test_good_url(client):
    responce = client.post(
        '/urls', data={'url': 'http://hexlet.io'}
    )
    assert responce.status_code == 302
