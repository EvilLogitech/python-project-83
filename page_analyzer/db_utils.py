import os
from psycopg2.extras import NamedTupleCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv
from contextlib import contextmanager


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
pool = None


def init_db_pool():
    return SimpleConnectionPool(0, 10, DATABASE_URL)


@contextmanager
def get_connection():
    global pool
    if not pool:
        pool = init_db_pool()
    connection = None
    try:
        connection = pool.getconn()
        yield connection
        connection.commit()
    except Exception as error:
        if connection:
            connection.rollback()
        raise error
    finally:
        if connection:
            pool.putconn(connection)


def is_url_in_base(url):
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=NamedTupleCursor)
        query = 'SELECT COUNT(*) FROM urls WHERE name=%s'
        data = (url,)
        cursor.execute(query, data)
        result = cursor.fetchone()
        cursor.close()
    return False if not result else (result.count > 0)


def get_url_id(url):
    with get_connection() as conn:
        id = None
        cursor = conn.cursor(cursor_factory=NamedTupleCursor)
        query = 'SELECT id FROM urls WHERE name=%s'
        data = (url, )
        cursor.execute(query, data)
        id = cursor.fetchone()
        cursor.close()
    return id.id if id else None


def get_urls_with_check_data():
    with get_connection() as conn:
        result = None
        cursor = conn.cursor(cursor_factory=NamedTupleCursor)
        query =  'SELECT '\
                't1.id, t1.name, t2.created_at, t2.status_code FROM '\
                '(SELECT id, name FROM urls ORDER BY id DESC) AS t1 '\
                'LEFT JOIN '\
                '(SELECT DISTINCT ON (url_id) '\
                'url_id, status_code, created_at FROM url_checks '\
                'ORDER BY url_id, created_at DESC) AS t2 '\
                'ON t1.id = t2.url_id'
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
    return result


def get_url_data(id):
    with get_connection() as conn:
        result = None
        cursor = conn.cursor(cursor_factory=NamedTupleCursor)
        query = 'SELECT * FROM urls WHERE id=%s'
        data = (id, )
        cursor.execute(query, data)
        result = cursor.fetchone()
        cursor.close()
    return result


def get_url_checks_data(id):
    with get_connection() as conn:
        result = None
        cursor = conn.cursor(cursor_factory=NamedTupleCursor)
        query = 'SELECT * FROM url_checks '\
                'WHERE url_id=%s ORDER BY id DESC'
        data = (id, )
        cursor.execute(query, data)
        result = cursor.fetchall()
        cursor.close()
    return result


def add_url(url):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = 'INSERT INTO urls (name) VALUES (%s)'
        data = (url, )
        cursor.execute(query, data)
        cursor.close()


def add_check_result(url_check_data):
    with get_connection() as conn:
        cursor = conn.cursor()
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
        cursor.close()
