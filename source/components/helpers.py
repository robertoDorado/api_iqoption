import mysql.connector
from datetime import datetime
import locale

cnx = mysql.connector.connect(user='labo_root', password='jB1bP1-8Cot%6+Kv',
                              host='45.90.108.177',
                              database='iqoption')

cursor = cnx.cursor()


def format_date():
    return datetime.now().strftime('%Y-%m-%d')

def format_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def persist_data(status: str, active: str, total_value: float, payoff: float, account_type: str):
    query = ("INSERT INTO operations (active, status, total_value, payoff, date, date_time, account_type) VALUES (%s, %s, %s, %s, %s, %s, %s)")
    data = (active, status, total_value, payoff, format_date(), format_datetime(), account_type)
    cursor.execute(query, data)
    cnx.commit()
    return


def count_registers(account_type: str):
    query = ("SELECT COUNT(*) as registers FROM operations WHERE date = %s AND account_type = %s")
    cursor.execute(query, (format_date(), account_type))
    return cursor.fetchone()


def count_win_registers(account_type: str):
    query = ("SELECT COUNT(*) as registers FROM operations WHERE status = 'win' AND date = %s AND account_type = %s")
    cursor.execute(query, (format_date(), account_type))
    return cursor.fetchone()


def count_loss_registers(account_type: str):
    query = ("SELECT COUNT(*) as registers FROM operations WHERE status = 'loose' AND date = %s AND account_type = %s")
    cursor.execute(query, (format_date(), account_type))
    return cursor.fetchone()


def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8') # definir o idioma para português do Brasil
    return locale.currency(value, grouping=True, symbol=None)