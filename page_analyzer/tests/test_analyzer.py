import page_analyzer as myapp
from bs4 import BeautifulSoup
import os


tests_path = os.path.dirname(__file__)


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


def test_html_parser_functions():
    right = get_html('right')
    assert myapp.get_h1(right) == 'Test header'
    assert myapp.get_title(right) == 'Right'
    assert myapp.get_description(right) == 'Test content'
    wrong = get_html('wrong')
    assert myapp.get_h1(wrong) == ''
    assert myapp.get_title(wrong) == ''
    assert myapp.get_description(wrong) == ''
