from flask import (Flask, redirect,
                   render_template,
                   request, flash,
                   get_flashed_messages
                   )
import validators
import psycopg2
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
def show_check_info(id):
    messages = get_flashed_messages(with_categories=True)
    query = 'SELECT * FROM urls WHERE id=%s'
    data = (id, )
    query_data = get_data_from_base(query, data)
    if not query_data:
        return render_template('404.html', messages={}, url=""), 404
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
    query = 'INSERT INTO url_checks '\
            '(url_id, status_code, h1, title, description) '\
            'VALUES (%s, %s, %s, %s, %s)'
    data = (id, '666', '', '', '',)
    insert_data_to_base(query, data)
    flash('Страница успешно проверена', 'success')
    return redirect(f'/urls/{id}'), 302


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
        conn = psycopg2.connect(DB_ACCESS)
        return conn
    except Exception as e:
        flash(e, 'danger')
