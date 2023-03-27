# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option
from candlestick import candlestick
import pandas as pd
from datetime import datetime

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)

wins = []
stop_loss = []

value = 1000
total_candles = 50

high_tendencie = False
low_tendencie = False
consolidated_market = False

otc = False
mkt = True

if otc:
    active_index = 76
elif mkt:
    active_index = 1

active = API.get_all_actives()[active_index]

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

time_exp = minute + 5

print(
    f'minha conta e {account_type}: R$ {balance}, horas: {hours}:{minutes}:{seconds} no ativo {active}')
print('iniciando algoritmo')

while True:

    # try:
    
    start = False

    second += 1

    if second > 59:
        minute += 1
        second = 0

    if minute > 59:
        hour += 1
        minute = 0

    if hour > 23:
        hour = 0
        minute = 0
        second = 0

    if minute == time_exp:

        active_index += 1

        if mkt and active_index > 6:
            active_index = 1

        if otc and active_index >= 82:
            active_index = 76

        active = API.get_all_actives()[active_index]
        historic_fifteen_minutes = API.get_realtime_candles(active, 900, total_candles)
        historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
        print(f'mudando o ativo para {active}')
        time_exp = minute + 5

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

    if len(red) > len(green):
        high_tendencie = False
        low_tendencie = True
        consolidated_market = False
        mkt_diff = len(red) - len(green)

    if len(red) < len(green):
        high_tendencie = True
        low_tendencie = False
        consolidated_market = False
        mkt_diff = len(green) - len(red)

    if len(red) == len(green):
        high_tendencie = False
        low_tendencie = False
        consolidated_market = True

    if consolidated_market:
        active_index += 1

        if mkt and active_index > 6:
            active_index = 1

        if otc and active_index >= 82:
            active_index = 76

        active = API.get_all_actives()[active_index]
        historic_fifteen_minutes = API.get_realtime_candles(active, 900, total_candles)
        historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
        print(f'mercado consolidado, mudando o ativo para {active}')

    # tomada de decisão em padrões de velas
    if high_tendencie and start and bullish_engulfing['result'][len(bullish_engulfing['result']) - 2] and all_candle_color_five_m[-1] == "green":
        print('engolfo de alta')
        API.call_decision(balance, value, active, wins, stop_loss,
                          all_candle_close_five_m[-1])
        active_index += 1

        if mkt and active_index > 6:
            active_index = 1

        if otc and active_index > 82:
            active_index = 76

        # active = API.get_all_actives()[active_index]
        # historic_fifteen_minutes = API.get_realtime_candles(active, 300, total_candles)
        # print(f'mudando para o ativo {active}')

    if high_tendencie and start and bullish_harami['result'][len(bullish_harami['result']) - 2] and all_candle_color_five_m[-1] == "green":
        print('harami de alta')
        API.call_decision(balance, value, active, wins, stop_loss,
                          all_candle_close_five_m[-1])
        active_index += 1

        if mkt and active_index > 6:
            active_index = 1

        if otc and active_index > 82:
            active_index = 76

        # active = API.get_all_actives()[active_index]
        # historic_fifteen_minutes = API.get_realtime_candles(active, 300, total_candles)
        # print(f'mudando o ativo para {active}')

    if low_tendencie and start and bearish_engulfing['result'][len(bearish_engulfing['result']) - 2] and all_candle_color_five_m[-1] == "red":
        print('engolfo de baixa')
        API.put_decision(balance, value, active, wins, stop_loss,
                         all_candle_close_five_m[-1])
        active_index += 1

        if mkt and active_index > 6:
            active_index = 1

        if otc and active_index > 82:
            active_index = 76

        # active = API.get_all_actives()[active_index]
        # historic_fifteen_minutes = API.get_realtime_candles(active, 300, total_candles)
        # print(f'mudando para o ativo {active}')

    if low_tendencie and start and bearish_harami['result'][len(bearish_harami['result']) - 2] and all_candle_color_five_m[-1] == "red":
        print('harami de baixa')
        API.put_decision(balance, value, active, wins, stop_loss,
                         all_candle_close_five_m[-1])
        active_index += 1

        if mkt and active_index > 6:
            active_index = 1

        if otc and active_index > 82:
            active_index = 76

        # active = API.get_all_actives()[active_index]
        # historic_fifteen_minutes = API.get_realtime_candles(active, 300, total_candles)
        # print(f'mudando o ativo para {active}')

    API.set_time_sleep(1)
    # except Exception as error:
    #     print(f'error: {error}')
