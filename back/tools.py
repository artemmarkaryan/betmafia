import telebot
from urllib import parse
import psycopg2
import pprint
import time

import config.settings

pp = pprint.PrettyPrinter().pprint

url = parse.urlparse(config.settings.database_url)
con = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)


bot = telebot.TeleBot(config.settings.token)


def report(**kwargs):
    pp(kwargs)


class DBConnection:
    def __init__(self, db_url):
        self.url = db_url
        self.con = None

    def __enter__(self):
        url = parse.urlparse(self.url)
        self.con = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        return self.con

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()
        self.con.close()


def set_(id_, table, column, value):
    with DBConnection(config.settings.database_url) as con:
        curs = con.cursor()
        curs.execute(f'UPDATE {table} SET {column} = %s WHERE id = {id_}', (value, ))
    report(action='set', id=id_, table=table, column=column, value=value)


def get(table, column=None, id_=None):

    if column is not None:

        if id_ is not None:

            with DBConnection(config.settings.database_url) as con:
                curs = con.cursor()
                curs.execute(f'select {column} from {table} where id = %s', (id_,))
                result = curs.fetchall()
                if len(result) == 1:
                    result = result[0]
                    if len(result) == 1:
                        result = result[0]
                else:
                    return None
                return result

        else:
            assert False, 'do not use column without id'

    else:  # column is None

        if id_ is not None:

            with DBConnection(config.settings.database_url) as con:
                curs = con.cursor()
                curs.execute(f'select * from {table} where id=%s', (id_,))
                data = curs.fetchall()
            columns = [column[0] for column in curs.description]
            result = []
            for line in data:
                result.append(dict(zip(columns, line)))
            return result if len(result) > 0 else None

        else:

            with DBConnection(config.settings.database_url) as con:
                curs = con.cursor()
                curs.execute(f'select * from {table}', (id_,))
                data = curs.fetchall()
            columns = [column[0] for column in curs.description]
            result = []
            for line in data:
                result.append(dict(zip(columns, line)))
            return result if len(result) > 0 else None


def delete(id_, table, column=None):

    with DBConnection(config.settings.database_url) as con:
        curs = con.cursor()

        if column is not None:
            curs.execute(f'update {table} set {column} = %s where id = %s', (None, id_))

        else:
            curs.execute(f'delete from {table} where id = %s', (id_, ))
    report(action='delete', table=table, column=column, id=id_)


def cols(table):
    with DBConnection(config.settings.database_url) as con:
        curs = con.cursor()
        curs.execute(f'select * from {table}')
    return [(col[0], col[1]) for col in curs.description]



def create_forecast():
    try:
        new_forecast_id = get('forecasts')[-1]['id'] + 1
    except NameError:
        new_forecast_id = 1
    except TypeError:
        new_forecast_id = 1

    with DBConnection(config.settings.database_url) as con:
        curs = con.cursor()
        curs.execute(f'insert into forecasts (id) values ({new_forecast_id})')

    return new_forecast_id


def date(day: int):
    date_ = time.strftime("%d.%m", time.gmtime(time.time() + 3600*24*day))
    return date_


def add_user(chat_id: int):
    with DBConnection(config.settings.database_url) as con:
        curs = con.cursor()
        curs.execute(f'insert into users (id) values ({chat_id})')
    report(action='add user', chat_id=chat_id)


def table_to_csv(table):
    cols_line = ''
    for col in cols(table):
        cols_line += ',' + col[0]
    cols_line = cols_line[1:]+',payment_id2'
    f = open('temp.csv', 'w')
    f.write(cols_line+'\n')
    curs = con.cursor()
    curs.copy_to(table=table, file=f, sep=',', null='Пусто')
    f.close()
