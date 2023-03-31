import mysql.connector

cnx = mysql.connector.connect(user='labo_root', password='jB1bP1-8Cot%6+Kv',
                              host='45.90.108.177',
                              database='iqoption')

cursor = cnx.cursor()


def persist_data(status: str, active: str, total_value: float):
    query = ("INSERT INTO operations (active, status, total_value) VALUES (%s, %s, %s)")
    data = (active, status, total_value)
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

