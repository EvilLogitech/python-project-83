import os
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


try:
    pool = ConnectionPool(DATABASE_URL)
except (Exception, psycopg.DatabaseError) as e:
    print("Error with Postgresql connection", e)


def is_url_in_base(url):
    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                query = 'SELECT COUNT(*) FROM urls WHERE name=%s'
                data = (url,)
                cursor.execute(query, data)
                result = cursor.fetchone()
            return True if result['count'] > 0 else False
    except psycopg.Error as e:
        print(e, 'danger')
    except psycopg.Warning as e:
        print(e, 'warning')


def get_url_id(url):
    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                query = 'SELECT id FROM urls WHERE name=%s'
                data = (url, )
                cursor.execute(query, data)
                id = cursor.fetchone()
                if id:
                    return id['id']
                return
    except psycopg.Error as e:
        print(e, 'danger')
    except psycopg.Warning as e:
        print(e, 'warning')


def get_urls_with_check_data():
    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                query = 'SELECT '\
                        't1.id, t1.name, t2.created_at, t2.status_code FROM '\
                        '(SELECT id, name FROM urls ORDER BY id DESC) AS t1 '\
                        'LEFT JOIN '\
                        '(SELECT DISTINCT ON (url_id) '\
                        'url_id, status_code, created_at FROM url_checks '\
                        'ORDER BY url_id, created_at DESC) AS t2 '\
                        'ON t1.id = t2.url_id'
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except psycopg.Error as e:
        print(e, 'danger')
    except psycopg.Warning as e:
        print(e, 'warning')


def get_url_data(id):
    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                query = 'SELECT * FROM urls WHERE id=%s'
                data = (id, )
                cursor.execute(query, data)
                result = cursor.fetchone()
                if result:
                    return result
                return
    except psycopg.Error as e:
        print(e, 'danger')
    except psycopg.Warning as e:
        print(e, 'warning')


def get_url_checks_data(id):
    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                query = 'SELECT * FROM url_checks '\
                        'WHERE url_id=%s ORDER BY id DESC'
                data = (id, )
                cursor.execute(query, data)
                result = cursor.fetchall()
                return result
    except psycopg.Error as e:
        print(e, 'danger')
    except psycopg.Warning as e:
        print(e, 'warning')


def add_url(url):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cursor:
                query = 'INSERT INTO urls (name) VALUES (%s)'
                data = (url, )
                cursor.execute(query, data)
    except psycopg.Error as e:
        print(e, 'danger')
    except psycopg.Warning as e:
        print(e, 'warning')


def add_check_result(url_check_data):
    try:
        with pool.connection() as conn:
            with conn.cursor() as cursor:
                query = 'INSERT INTO url_checks '\
                        '(url_id, status_code, h1, title, description) '\
                        'VALUES (%s, %s, %s, %s, %s)'
                data = (
                    url_check_data['id'],
                    url_check_data['status_code'],
                    url_check_data['h1'],
                    url_check_data['title'],
                    url_check_data['description'],
                )
                cursor.execute(query, data)
    except psycopg.Error as e:
        print(e, 'danger')
    except psycopg.Warning as e:
        print(e, 'warning')
