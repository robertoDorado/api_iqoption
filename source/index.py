# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option
from candlestick import candlestick
import pandas as pd
from datetime import datetime
import mysql.connector
import numpy as np

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


account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)

wins = []
stop_loss = []

total_candles = 20

high_tendencie = False
low_tendencie = False
consolidated_market = False

otc = True
mkt = False

if otc:
    active_index = 76
elif mkt:
    active_index = 1

total_registers = count_registers()[0]
total_win = count_win_registers()[0]
total_loss = count_loss_registers()[0]

active_type = 'turbo'
active = API.get_all_actives()[active_index]
payoff = API.get_profit(active, active_type) * 100

fraction = API.kelly(payoff, round(total_win
                     / total_registers, 2), round(total_loss / total_registers, 2))
value = round(balance * fraction, 2)

decimal = 5

total_candles_df = total_candles
new_candle = []

time = datetime.now()
hour = time.hour
minute = time.minute
second = time.second

if hour < 10:
    hours = f'0{hour}'
elif hour >= 10:
    hours = hour

if minute < 10:
    minutes = f'0{minute}'
elif minute >= 10:
    minutes = minute

if second < 10:
    seconds = f'0{second}'
elif second >= 10:
    seconds = second

print(f'minha conta e {account_type}: R$ {balance}, ativo: {active}, payoff de {payoff}%, horas: {hours}:{minutes}:{seconds}')
print('iniciando algoritmo')

while True:

    start = False

    historic_fifteen_minutes = API.get_realtime_candles(active, 900, total_candles)
    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)

    historic_fifteen_minutes = [{'candle': 'red' if historic_fifteen_minutes[i]['open'] > historic_fifteen_minutes[i]['close']
                                 else 'green' if historic_fifteen_minutes[i]['close'] > historic_fifteen_minutes[i]['open'] else 'dogi',
                                 'close': historic_fifteen_minutes[i]['close'], 'open': historic_fifteen_minutes[i]['open'],
                                 'max': historic_fifteen_minutes[i]['max'], 'min': historic_fifteen_minutes[i]['min'], 'id': historic_fifteen_minutes[i]['id']}
                                for i in historic_fifteen_minutes]

    historic_five_minutes = [{'candle': 'red' if historic_five_minutes[i]['open'] > historic_five_minutes[i]['close']
                              else 'green' if historic_five_minutes[i]['close'] > historic_five_minutes[i]['open'] else 'dogi',
                              'close': historic_five_minutes[i]['close'], 'open': historic_five_minutes[i]['open'],
                              'max': historic_five_minutes[i]['max'], 'min': historic_five_minutes[i]['min'], 'id': historic_five_minutes[i]['id']}
                             for i in historic_five_minutes]

    candles = API.get_all_candles(active, 300, total_candles_df)

    # calcular a média móvel simples (SMA) dos últimos n períodos
    prices = np.array([candle['close'] for candle in candles])
    sma = np.mean(prices)

    # comparar o preço atual com a SMA para determinar a tendência de mercado
    current_price = [i['close'] for i in historic_five_minutes]
    
    if current_price[-1] > sma:
        trend = 'high'
    elif current_price[-1] < sma:
        trend = 'low'
    else:
        consolidated_market = True

    candles_df = pd.DataFrame.from_dict(candles)
    candles_df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)

    bearish_harami = candlestick.bearish_harami(candles_df, target='result')
    bearish_harami = bearish_harami.to_dict()

    bullish_harami = candlestick.bullish_harami(candles_df, target='result')
    bullish_harami = bullish_harami.to_dict()

    bearish_engulfing = candlestick.bearish_engulfing(candles_df, target='result')
    bearish_engulfing = bearish_engulfing.to_dict()

    bullish_engulfing = candlestick.bullish_engulfing(candles_df, target='result')
    bullish_engulfing = bullish_engulfing.to_dict()
    
    hanging_man = candlestick.hanging_man(candles_df, target='result')
    hanging_man = hanging_man.to_dict()
    
    hammer = candlestick.hammer(candles_df, target='result')
    hammer = hammer.to_dict()

    all_candle_max_five_m = [i['max'] for i in historic_five_minutes]
    all_candle_min_five_m = [i['min'] for i in historic_five_minutes]
    all_candle_open_five_m = [i['open'] for i in historic_five_minutes]
    all_candle_close_five_m = [i['close'] for i in historic_five_minutes]
    all_candle_color_five_m = [i['candle'] for i in historic_five_minutes]
    all_candle_id_five_m = [i['id'] for i in historic_five_minutes]

    red = [i['candle'] for i in historic_fifteen_minutes if i['candle'] == 'red']
    green = [i['candle'] for i in historic_fifteen_minutes if i['candle'] == 'green']

    if len(new_candle) < 1:
        new_candle.append(all_candle_id_five_m[-1])

    if new_candle[0] == all_candle_id_five_m[-2]:
        new_candle = []
        start = True

    if consolidated_market:
        active_index += 1

        if mkt and active_index > 6:
            active_index = 1

        if otc and active_index >= 82:
            active_index = 76

        active = API.get_all_actives()[active_index]
        historic_fifteen_minutes = API.get_realtime_candles(active, 900, total_candles)
        historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
        payoff = API.get_profit(active, active_type) * 100
        print(
            f'mercado consolidado, mudando o ativo para {active}, payoff de {payoff}%, horas: {hours}:{minutes}:{seconds}')

    # tomada de decisão em padrões de velas
    if trend == 'low' and start and bullish_engulfing['result'][len(bullish_engulfing['result']) - 2] and all_candle_color_five_m[-1] == 'green':
        print('engolfo de alta')
        status = API.call_decision(balance, value, active, wins, stop_loss)
        persist_data(status, active, round(
            value * API.get_profit(active, active_type), 2), payoff)

    if trend == 'low' and start and bullish_harami['result'][len(bullish_harami['result']) - 2] and all_candle_color_five_m[-1] == 'green':
        print('harami de alta')
        status = API.call_decision(balance, value, active, wins, stop_loss)
        persist_data(status, active, round(
            value * API.get_profit(active, active_type), 2), payoff)

    if trend == 'high' and start and bearish_engulfing['result'][len(bearish_engulfing['result']) - 2] and all_candle_color_five_m[-1] == 'red':
        print('engolfo de baixa')
        status = API.put_decision(balance, value, active, wins, stop_loss)
        persist_data(status, active, round(
            value * API.get_profit(active, active_type), 2), payoff)

    if trend == 'high' and start and bearish_harami['result'][len(bearish_harami['result']) - 2] and all_candle_color_five_m[-1] == 'red':
        print('harami de baixa')
        status = API.put_decision(balance, value, active, wins, stop_loss)
        persist_data(status, active, round(
            value * API.get_profit(active, active_type), 2), payoff)
    
    if trend == 'high' and start and hanging_man['result'][len(hanging_man['result']) - 2] and all_candle_color_five_m[-1] == 'red':
        print('enforcado')
        status = API.put_decision(balance, value, active, wins, stop_loss)
        persist_data(status, active, round(
            value * API.get_profit(active, active_type), 2), payoff)
        
    if trend == 'low' and start and hammer['result'][len(hammer['result']) - 2] and all_candle_color_five_m[-1] == 'green':
        print('martelo')
        status = API.call_decision(balance, value, active, wins, stop_loss)
        persist_data(status, active, round(
            value * API.get_profit(active, active_type), 2), payoff)

    API.set_time_sleep(1)
