import mysql.connector
from datetime import datetime

cnx = mysql.connector.connect(user='labo_root', password='jB1bP1-8Cot%6+Kv',
                              host='45.90.108.177',
                              database='iqoption')

cursor = cnx.cursor()


def format_date():
    return datetime.now().strftime('%Y-%m-%d')

def format_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def persist_data(status: str, active: str, total_value: float, payoff: float):
    query = ("INSERT INTO operations (active, status, total_value, payoff, date, date_time) VALUES (%s, %s, %s, %s, %s, %s)")
    data = (active, status, total_value, payoff, format_date(), format_datetime())
    cursor.execute(query, data)
    cnx.commit()
    return


def count_registers():
    query = ("SELECT COUNT(*) as registers FROM operations")
    cursor.execute(query)
    return cursor.fetchone()


def count_win_registers():
    query = ("SELECT COUNT(*) as registers FROM operations WHERE status = 'win'")
    cursor.execute(query)
    return cursor.fetchone()


def count_loss_registers():
    query = ("SELECT COUNT(*) as registers FROM operations WHERE status = 'loose'")
    cursor.execute(query)
    return cursor.fetchone()

