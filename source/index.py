# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from random import choices
from datetime import datetime

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

balance = API.balance(account_type)
print(f'my account is {account_type}: R$ {balance}')


while True:
    
    try:
        five_minutes_candle = API.get_all_candles('EURUSD', 300, 1)
        fifteen_minutes_candle = API.get_all_candles('EURUSD', 900, 1)
        
        candle_fifteen_m = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi', 'open': i['open'], 'close': i['close']}
        for i in fifteen_minutes_candle]
        
        candle_five_m = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi', 'open': i['open'], 'close': i['close']}
        for i in five_minutes_candle]
        
        print(candle_fifteen_m)
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')