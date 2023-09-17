import os
import psycopg2
from psycopg2.extras import NamedTupleCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


pool = None  # TestPlug
try:
    pool = SimpleConnectionPool(0, 10, DATABASE_URL)
except (Exception, psycopg2.DatabaseError) as e:
    print("Error with Postgresql connection", e)


def is_url_in_base(url):
    try:
        conn = pool.getconn()
        try:
            cursor = conn.cursor(cursor_factory=NamedTupleCursor)
            query = 'SELECT COUNT(*) FROM urls WHERE name=%s'
            data = (url,)
            cursor.execute(query, data)
            result = cursor.fetchone()
            cursor.close()
        finally:
            pool.putconn(conn)
        print(result)
        return False if not result else (result.count > 0)
    except psycopg2.Error as e:
        print(e, 'danger')
    except psycopg2.Warning as e:
        print(e, 'warning')


def get_url_id(url):
    try:
        conn = pool.getconn()
        id = None
        try:
            cursor = conn.cursor(cursor_factory=NamedTupleCursor)
            query = 'SELECT id FROM urls WHERE name=%s'
            data = (url, )
            cursor.execute(query, data)
            id = cursor.fetchone()
            cursor.close()
        finally:
            pool.putconn(conn)
        return id.id if id else None
    except psycopg2.Error as e:
        print(e, 'danger')
    except psycopg2.Warning as e:
        print(e, 'warning')


def get_urls_with_check_data():
    try:
        conn = pool.getconn()
        result = None
        try:
            cursor = conn.cursor(cursor_factory=NamedTupleCursor)
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
            cursor.close()
        finally:
            pool.putconn(conn)
        return result
    except psycopg2.Error as e:
        print(e, 'danger')
    except psycopg2.Warning as e:
        print(e, 'warning')


def get_url_data(id):
    try:
        conn = pool.getconn()
        result = None
        try:
            cursor = conn.cursor(cursor_factory=NamedTupleCursor)
            query = 'SELECT * FROM urls WHERE id=%s'
            data = (id, )
            cursor.execute(query, data)
            result = cursor.fetchone()
            cursor.close()
        finally:
            pool.putconn(conn)
        return result
    except psycopg2.Error as e:
        print(e, 'danger')
    except psycopg2.Warning as e:
        print(e, 'warning')


def get_url_checks_data(id):
    try:
        conn = pool.getconn()
        result = None
        try:
            cursor = conn.cursor(cursor_factory=NamedTupleCursor)
            query = 'SELECT * FROM url_checks '\
                    'WHERE url_id=%s ORDER BY id DESC'
            data = (id, )
            cursor.execute(query, data)
            result = cursor.fetchall()
            cursor.close()
        finally:
            pool.putconn(conn)
        return result
    except psycopg2.Error as e:
        print(e, 'danger')
    except psycopg2.Warning as e:
        print(e, 'warning')


def add_url(url):
    try:
        conn = pool.getconn()
        try:
            cursor = conn.cursor()
            query = 'INSERT INTO urls (name) VALUES (%s)'
            data = (url, )
            cursor.execute(query, data)
            conn.commit()
            cursor.close()
        finally:
            pool.putconn(conn)
    except psycopg2.Error as e:
        print(e, 'danger')
    except psycopg2.Warning as e:
        print(e, 'warning')


def add_check_result(url_check_data):
    try:
        conn = pool.getconn()
        try:
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
            conn.commit()
            cursor.close()
        finally:
            pool.putconn(conn)
    except psycopg2.Error as e:
        print(e, 'danger')
    except psycopg2.Warning as e:
        print(e, 'warning')
