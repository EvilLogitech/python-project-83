import page_analyzer as myapp
import pytest
import os


tests_path = os.path.dirname(__file__)


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


def get_html(filename):
    filepath = f'{tests_path}/fixtures/{filename}.html'
    with open(filepath) as f:
        file_data = f.read()
    return file_data


def test_templates(client):
    responce = client.get('/')
    assert bytes(
        '<title>Анализатор страниц</title>', 'utf-8'
    ) in responce.data
    # assert bytes(
    #     '<a href="https://ru.hexlet.io/">Hexlet</a>', 'utf-8'
    # ) in responce.data
    # responce = client.get('/urls')
    # assert bytes(
    #     '<th>Последняя проверка</th>', 'utf-8'
    # ) in responce.data


# testdata = [
#     (
#         'wrong url',
#         bytes('Некорректный URL', 'utf-8')
#     ),
#     (
#         f'http://{"very"*70}longurl.ru',
#         bytes('URL превышает 255 символов', 'utf-8')
#     ),
#     (
#         'Another bad url',
#         bytes('<div class="alert alert-danger" role="alert">', 'utf-8')
#     )
# ]


# @pytest.mark.parametrize("input, expected", testdata)
# def test_validator(client, input, expected):
#     responce = client.post(
#         '/urls', data={'url': input}
#     )
#     assert expected in responce.data


# def test_good_url(client):
#     responce = client.post(
#         '/urls', data={'url': 'http://hexlet.io'}
#     )
#     assert responce.status_code == 302
