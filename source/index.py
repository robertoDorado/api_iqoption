# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option
from datetime import datetime
import numpy as np
from components.helpers import *

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

if value >= 20000:
    value = value / 2

total_candles_df = total_candles
new_candle = []

time = datetime.now()
hour = time.hour
minute = time.minute
second = time.second

threshold = 0.5

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
    
    # Definir níveis de suporte e resistência
    support = min([i['close'] for i in candles])
    resistance = max([i['close'] for i in candles])
    
    # tomada decisão pullback
    # Verificar se o preço está abaixo da SMA
    # Se estiver abaixo, verificar se o preço chegou ao nível de suporte
    if [i['close'] for i in candles][-1] < sma and [i['close'] for i in candles][-1] <= support + threshold and start:
        print(f"Pullback detectado! compra no valor de {value}")
        
        if value >= 20000:
            value = value / 2
            
        status = API.call_decision(balance, value, active, wins, stop_loss)
        if status == 'win':
            register_value = value * API.get_profit(active, active_type)
        else:
            register_value = value
            
        persist_data(status, active, round(register_value, 2), payoff)
        balance = API.balance(account_type)
        fraction = API.kelly(payoff, round(total_win / total_registers, 2), round(total_loss / total_registers, 2))
        value = round(balance * fraction, 2)
        
    # Se estiver acima, verificar se o preço chegou ao nível de resistência
    elif [i['close'] for i in candles][-1] >= resistance - threshold and start:
            print(f"Pullback detectado! venda no valor de {value}")
            
            if value >= 20000:
                value = value / 2
                
            status = API.put_decision(balance, value, active, wins, stop_loss)
            if status == 'win':
                register_value = value * API.get_profit(active, active_type)
            else:
                register_value = value
                
            persist_data(status, active, round(register_value, 2), payoff)
            balance = API.balance(account_type)
            fraction = API.kelly(payoff, round(total_win / total_registers, 2), round(total_loss / total_registers, 2))
            value = round(balance * fraction, 2)
        
    API.set_time_sleep(1)