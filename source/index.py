# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option
from candlestick import candlestick
import pandas as pd
from datetime import datetime

account_type = "REAL"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)

wins = []
stop_loss = []

value = balance * 0.1
total_candles = 30

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

seconds = 0
decimal = 5
mkt_diff = 0

total_candles_df = total_candles
new_candle = []

time = datetime.now()
hour = time.hour
minutes = time.minute
seconds = time.second

print(f'my account is {account_type}: R$ {balance}, horas: {hour}:{minutes}:{seconds} no ativo {active}')
print('iniciando algoritimo')

while True:

    try:

        start = False
        seconds += 1

        if seconds == 300:

            seconds = 0
            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)

        historic_five_minutes = [{'candle': 'red' if historic_five_minutes[i]['open'] > historic_five_minutes[i]['close']
        else 'green' if historic_five_minutes[i]['close'] > historic_five_minutes[i]['open'] else 'dogi',
        'close': historic_five_minutes[i]['close'], 'open': historic_five_minutes[i]['open'],
        'max': historic_five_minutes[i]['max'], 'min': historic_five_minutes[i]['min'], 'id': historic_five_minutes[i]['id']}
        for i in historic_five_minutes]

        candles = API.get_all_candles(active, 300, total_candles_df)

        candles_df = pd.DataFrame.from_dict(candles)
        candles_df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)

        hammer = candlestick.hammer(candles_df, target='result')
        hammer = hammer.to_dict()

        inverted_hammer = candlestick.inverted_hammer(candles_df, target='result')
        inverted_hammer = inverted_hammer.to_dict()

        shooting_star = candlestick.shooting_star(candles_df, target='result')
        shooting_star = shooting_star.to_dict()

        hanging_man = candlestick.hanging_man(candles_df, target='result')
        hanging_man = hanging_man.to_dict()

        bearish_harami = candlestick.bearish_harami(candles_df, target='result')
        bearish_harami = bearish_harami.to_dict()

        bullish_harami = candlestick.bullish_harami(candles_df, target='result')
        bullish_harami = bullish_harami.to_dict()

        bearish_engulfing = candlestick.bearish_engulfing(candles_df, target='result')
        bearish_engulfing = bearish_engulfing.to_dict()

        bullish_engulfing = candlestick.bullish_engulfing(candles_df, target='result')
        bullish_engulfing = bullish_engulfing.to_dict()

        piercing_pattern = candlestick.piercing_pattern(candles_df, target='result')
        piercing_pattern = piercing_pattern.to_dict()

        dark_cloud_cover = candlestick.dark_cloud_cover(candles_df, target='result')
        dark_cloud_cover = dark_cloud_cover.to_dict()

        all_candle_max_five_m = [i['max'] for i in historic_five_minutes]
        all_candle_min_five_m = [i['min'] for i in historic_five_minutes]
        all_candle_open_five_m = [i['open'] for i in historic_five_minutes]
        all_candle_close_five_m = [i['close'] for i in historic_five_minutes]
        all_candle_color_five_m = [i['candle'] for i in historic_five_minutes]
        all_candle_id_five_m = [i['id'] for i in historic_five_minutes]

        first_candle_index = len(all_candle_close_five_m) - 1
        second_candle_index = len(all_candle_close_five_m) - 2
        third_candle_index = len(all_candle_close_five_m) - 3

        red = [i['candle'] for i in historic_five_minutes if i['candle'] == 'red']
        green = [i['candle'] for i in historic_five_minutes if i['candle'] == 'green']

        if len(new_candle) < 1:
            new_candle.append(all_candle_id_five_m[first_candle_index])

        if new_candle[0] == all_candle_id_five_m[second_candle_index]:
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
                
            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mercado consolidado, mudando para o ativo {active}')
        
        if mkt_diff == 2 or mkt_diff == 3:
            active_index += 1
            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mercado consolidado, mudando para o ativo {active}')

        # tomada de decisão em padrões de velas
        if low_tendencie and start and bullish_engulfing['result'][second_candle_index] == True:
            print('engolfo de alta')
            API.call_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1
              
            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if low_tendencie and start and bullish_harami['result'][second_candle_index] == True:
            print('harami de alta')
            API.call_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if low_tendencie and start and hammer['result'][second_candle_index] == True:
            print('martelo')
            API.call_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if low_tendencie and start and inverted_hammer['result'][second_candle_index] == True:
            print('martelo invertido')
            API.call_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if low_tendencie and start and piercing_pattern['result'][second_candle_index] == True:
            print('piercing')
            API.call_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if high_tendencie and start and bearish_engulfing['result'][second_candle_index] == True:
            print('engolfo de baixa')
            API.put_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if high_tendencie and start and bearish_harami['result'][second_candle_index] == True:
            print('harami de baixa')
            API.put_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if high_tendencie and start and shooting_star['result'][second_candle_index] == True:
            print('estrela cadente')
            API.put_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if high_tendencie and start and hanging_man['result'][second_candle_index] == True:
            print('enforcado')
            API.put_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')

        if high_tendencie and start and dark_cloud_cover['result'][second_candle_index] == True:
            print('nuvem negra')
            API.put_decision(balance, value, active, wins, stop_loss)

            active_index += 1
            
            if mkt and active_index > 6:
                active_index = 1

            active = API.get_all_actives()[active_index]
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')



        print('processando')
        API.set_time_sleep(1)
    except Exception as error:
        print(f'exception: {error}')
