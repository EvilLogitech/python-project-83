from page_analyzer.db_utils import (get_url_id, get_url_data,
                                    get_url_checks_data,
                                    get_urls_with_check_data,
                                    is_url_in_base, add_url,
                                    add_check_result)
from flask import (Flask, redirect, render_template, abort,
                   request, flash, get_flashed_messages)
import os
import requests
import validators
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.get('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages, url="")


@app.post('/')
@app.post('/urls')
def add_site():
    url = request.form.get('url', '')
    errors = validate_url(url)
    if errors:
        flash(errors, 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages, url=url), 422
    url = parse_url(url)
    if is_url_in_base(url):
        flash('Страница уже существует', 'info')
    else:
        add_url(url)
        flash('Страница успешно добавлена', 'success')
    id = get_url_id(url)
    return redirect(f'/urls/{id}'), 302


@app.get('/urls')
def urls():
    sites = get_urls_with_check_data()
    return render_template('urls.html', sites=sites)


@app.get('/urls/<id>')
def show_url_info(id):
    messages = get_flashed_messages(with_categories=True)
    site = get_url_data(id)
    if not site:
        abort(404)
    checks = get_url_checks_data(id)
    return render_template(
        'check_result.html',
        site=site,
        checks=checks,
        messages=messages
    )


@app.post('/urls/<id>/checks')
def make_url_check(id):
    url_data = get_url_data(id)
    if not url_data:
        abort(404)
    status_code = 500
    try:
        req = requests.get(url_data['name'])
        status_code = req.status_code
    except Exception:
        pass
    if status_code > 200:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        url_check_data = {'status_code': status_code, 'id': id}
        url_check_data = url_check_data | get_parsed_data(req.text)
        add_check_result(url_check_data)
        flash('Страница успешно проверена', 'success')
    return redirect(f'/urls/{id}'), 302


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


def get_date(date):
    return date.date() if date else ''


def validate_url(url):
    if len(url) > 255:
        return 'URL превышает 255 символов'
    if not validators.url(url):
        return 'Некорректный URL'


def parse_url(url):
    parsed = urlparse(url)
    return f'{parsed.scheme}://{parsed.hostname}'


def get_parsed_data(html_text):
    html = BeautifulSoup(html_text, 'html.parser')
    parsed_data = {}
    tag = html.find('h1')
    parsed_data['h1'] = tag.text if tag else ''
    tag = html.find('meta', {'name': 'description'})
    parsed_data['description'] = tag.get('content') if tag else ''
    tag = html.find('title')
    parsed_data['title'] = tag.string if tag else ''
    return parsed_data
