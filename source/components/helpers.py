from datetime import datetime, date, timedelta
import locale
from itertools import cycle

def remove_index(current_index, active_index):
    if current_index in active_index:
        active_index.remove(current_index)
    index_iter = cycle(active_index)
    return index_iter

def format_date():
    return date.today()

def format_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def format_currency(value):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8') # definir o idioma para português do Brasil
    return locale.currency(value, grouping=True, symbol="R$")