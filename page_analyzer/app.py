from flask import (Flask, redirect,
                   render_template,
                   request, flash,
                   get_flashed_messages,
                   abort)
import requests
import validators
import psycopg2
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.get('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages, url="")


@app.post('/')
def add_site():
    url = request.form.get('url', '')
    errors = validate_url(url)
    if errors:
        flash(errors, 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages, url=url), 422
    url = parse_url(url)
    if not check_url_in_base(url):
        query = 'INSERT INTO urls (name) VALUES (%s)'
        data = (url, )
        insert_data_to_base(query, data)
        flash('Страница успешно добавлена', 'success')
    query = 'SELECT id FROM urls WHERE name=%s'
    data = (url, )
    id = get_data_from_base(query, data)[0][0]
    return redirect(f'/urls/{id}'), 302


@app.get('/urls')
def urls():
    # query = 'SELECT * FROM urls ORDER BY id DESC'
    sites = []
    query = 'SELECT t1.id, t1.name, t2.created_at, t2.status_code FROM '\
            '(SELECT id, name FROM urls ORDER BY id DESC) AS t1 '\
            'LEFT JOIN '\
            '(SELECT DISTINCT ON (url_id) '\
            'url_id, status_code, created_at FROM url_checks '\
            'ORDER BY url_id, created_at DESC) AS t2 '\
            'ON t1.id = t2.url_id'
    urls_ = get_data_from_base(query, ())
    for item in urls_:
        sites.append(
            {
                "id": item[0],
                "name": item[1],
                "created_at": get_date(item[2]),
                "status_code": item[3] or ''
            }
        )
    return render_template('urls.html', sites=sites)


@app.get('/urls/<id>')
def show_url_info(id):
    messages = get_flashed_messages(with_categories=True)
    query = 'SELECT * FROM urls WHERE id=%s'
    data = (id, )
    query_data = get_data_from_base(query, data)
    if not query_data:
        abort(404)
    query_data = query_data[0]
    site = {
        "id": query_data[0],
        "name": query_data[1],
        "created_at": get_date(query_data[2])
    }
    query = 'SELECT * FROM url_checks WHERE url_id=%s ORDER BY id DESC'
    data = (id, )
    query_data = get_data_from_base(query, data)
    checks = []
    for check in query_data:
        checks.append(
            {
                "id": check[0],
                "status_code": check[2],
                "h1": check[3],
                "title": check[4],
                "description": check[5],
                "created_at": get_date(check[6])
            }
        )
    return render_template(
        'check_result.html',
        site=site,
        checks=checks,
        messages=messages
    )


@app.post('/urls/<id>/checks')
def make_url_check(id):
    query = 'SELECT name FROM urls WHERE id=%s'
    data = (id,)
    query_data = get_data_from_base(query, data)
    if not query_data:
        abort(404)
    url = query_data[0][0]
    status_code = 500
    try:
        req = requests.get(url)
        status_code = req.status_code
    except Exception:
        pass
    if status_code > 200:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        html_document = BeautifulSoup(req.text, 'html.parser')
        h1 = get_h1(html_document)
        title = get_title(html_document)
        meta_description = get_description(html_document)
        query = 'INSERT INTO url_checks '\
                '(url_id, status_code, h1, title, description) '\
                'VALUES (%s, %s, %s, %s, %s)'
        data = (id, status_code, h1, title, meta_description,)
        insert_data_to_base(query, data)
        flash('Страница успешно проверена', 'success')
    return redirect(f'/urls/{id}'), 302


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


def get_date(date):
    return date.date() if date else ''


def validate_url(url_):
    if len(url_) > 255:
        return 'URL превышает 255 символов'
    if not validators.url(url_):
        return 'Некорректный URL'


def parse_url(url):
    parsed = urlparse(url)
    return f'{parsed.scheme}://{parsed.hostname}'


def get_data_from_base(query, data):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except psycopg2.Error as e:
        flash(e, 'danger')
    except psycopg2.Warning as e:
        flash(e, 'info')


def insert_data_to_base(query, data):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        conn.commit()
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        flash(e, 'danger')
    except psycopg2.Warning as e:
        flash(e, 'warning')


def check_url_in_base(url):
    query = 'SELECT COUNT(*) FROM urls WHERE name=%s'
    data = (url,)
    result = get_data_from_base(query, data)[0][0]
    if result == 0:
        return False
    flash('Страница уже существует', 'info')
    return True


def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        flash(e, 'danger')


def get_h1(html):
    tag = html.find('h1')
    return tag.text if tag else ''


def get_description(html):
    tag = html.find('meta', {'name': 'description'})
    return tag.get('content') if tag else ''


def get_title(html):
    tag = html.find('title')
    return tag.string if tag else ''
