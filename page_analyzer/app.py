from flask import (Flask, redirect,
                   render_template,
                   request, flash,
                   get_flashed_messages
                   )
import validators
import psycopg2
import datetime
from urllib.parse import urlparse
from dotenv import dotenv_values


ENV_VALUES = dotenv_values()
DB_ACCESS = ENV_VALUES.get('DB_ACCESS')
app = Flask(__name__)
app.secret_key = ENV_VALUES.get('SECRET_KEY')


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
        add_url_to_base(url)
    query = 'SELECT id FROM urls WHERE name=%s'
    data = (url, )
    id = get_data_from_base(query, data)[0][0]
    return redirect(f'urls/{id}'), 302


@app.get('/urls')
def urls():
    query = 'SELECT * FROM urls ORDER BY id DESC'
    sites = []
    urls_ = get_data_from_base(query, ())
    for item in urls_:
        sites.append(
            {
                "id": item[0],
                "name": item[1],
                "created_at": 'NOT NOW',
                "responce_code": get_date(item[2])
            }
        )
    return render_template('urls.html', sites=sites)


@app.get('/urls/<id>')
def show_check_info(id):
    messages = get_flashed_messages(with_categories=True)
    query = 'SELECT * FROM urls WHERE id=%s'
    data = (id, )
    url_data = get_data_from_base(query, data)[0]
    site = {
        "id": url_data[0],
        "name": url_data[1],
        "created_at": get_date(url_data[2])
    }
    checks = [{
        "id": "1",
        "responce_code": "200",
        "h1": "Хедерище",
        "title": "Заголовище",
        "description": "Тестовая днина",
        "created_at": "1666-01-02"
    }]
    return render_template(
        'check_result.html',
        site=site,
        checks=checks,
        messages=messages
    )


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


def add_url_to_base(url):
    query = 'INSERT INTO urls (name, created_at) VALUES (%s, %s)'
    data = (url, datetime.date.today())
    insert_data_to_base(query, data)
    flash('Страница успешно добавлена', 'success')


def get_connection():
    try:
        conn = psycopg2.connect(DB_ACCESS)
        return conn
    except Exception as e:
        flash(e, 'danger')
