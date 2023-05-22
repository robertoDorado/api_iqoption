import mysql.connector
from datetime import datetime, date, timedelta
import locale

cnx = mysql.connector.connect(user='labo_root', password='jB1bP1-8Cot%6+Kv',
                              host='45.90.108.177',
                              database='iqoption')

cursor = cnx.cursor()


def format_date():
    return date.today()

def format_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def persist_data(status, active, total_value, payoff, account_type, balance):
    query = ("INSERT INTO operations (active, status, total_value, payoff, date, date_time, account_type, balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    data = (active, status, total_value, payoff, format_date(), format_datetime(), account_type, balance)
    cursor.execute(query, data)
    cnx.commit()
    return

def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8') # definir o idioma para português do Brasil
    return locale.currency(value, grouping=True, symbol=None)

def get_first_register_balance(set_day):
    filter_date = format_date() - timedelta(days=set_day)
    query = ("SELECT balance FROM operations WHERE date = %s ORDER BY id DESC LIMIT 1")
    cursor.execute(query, (filter_date,))
    return cursor.fetchone()

def count_registers():
    query = ("SELECT COUNT(*) as registers FROM operations")
    cursor.execute(query)
    return cursor.fetchone()
    