# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from datetime import datetime
import numpy as np
from components.helpers import *
import getpass
import re

email_iqoption = input('e-mail iqoption: ')
password_iqoption = getpass.getpass(prompt='senha iqoption: ')
account_type = input('tipo de conta (practice/real): ')

if account_type == "real":
    account_type = account_type.upper()
elif account_type == "practice":
    account_type = account_type.upper()
else:
    print('tipo de conta inválido')
    exit()

API = BOT_IQ_Option(account_type, email_iqoption, password_iqoption)

if API.check_my_connection() == False:
    print('erro na conexão com a corretora')
    exit()

try:
    goal_win = int(input('quantas tentativas de ganho: '))
    goal_loss = int(input('quantas tentativas de perda: '))
except ValueError:
    print('meta inválida')
    exit()

try:
    goal = input('qual será a sua meta: ')
    is_comma = True if re.match(r"\d+,\d+", goal) else False
    goal = re.sub(r",", ".", goal) if is_comma else goal
    goal = float(goal)
except ValueError:
    print('valor inválido')

instance = API.get_instance()
balance = API.balance(account_type)

total_candles = 15

market = input('qual será o mercado (otc/mkt): ')
mkt = True if market == 'mkt' else False
otc = True if market == 'otc' else False

if mkt == False and otc == False:
    print('tipo de mercado inválido')
    exit()

if otc:
    active_index = 76
elif mkt:
    active_index = 1

active_type = 'turbo'
active = API.get_all_actives()[active_index]
payoff = API.get_profit(active, active_type) * 100

try:
    value = input('qual será o primeiro valor de entrada: ')
    is_comma = True if re.match(r"\d+,\d+", value) else False
    value = re.sub(r",", ".", value) if is_comma else value
    value = float(value)
except ValueError:
    print('formato inválido')
    exit()
    
if value >= 20000:
    value = 20000

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

wins = []
loss = []

print(f'minha conta e {account_type}: R$ {format_currency(balance)}, ativo: {active}, payoff de {payoff}%, horas: {hours}:{minutes}:{seconds}, gerenciamento: {goal_win}X{goal_loss}')
print('processando algoritmo')

while True:

    start = False

    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles_df)

    historic_five_minutes = [{'candle': 'red' if historic_five_minutes[i]['open'] > historic_five_minutes[i]['close']
                              else 'green' if historic_five_minutes[i]['close'] > historic_five_minutes[i]['open'] else 'dogi',
                              'close': historic_five_minutes[i]['close'], 'open': historic_five_minutes[i]['open'],
                              'max': historic_five_minutes[i]['max'], 'min': historic_five_minutes[i]['min'], 'id': historic_five_minutes[i]['id']}
                             for i in historic_five_minutes]

    candles = API.get_all_candles(active, 300, total_candles_df)

    # calcular a média móvel simples (SMA) dos últimos n períodos
    prices = np.array([candle['close'] for candle in candles]).astype(float)
    sma = np.mean(prices)

    # comparar o preço atual com a SMA para determinar a tendência de mercado
    current_price = [i['close'] for i in historic_five_minutes]

    all_candle_id_five_m = [i['id'] for i in historic_five_minutes]

    if len(new_candle) < 1:
        new_candle.append(all_candle_id_five_m[-1])

    if new_candle[0] == all_candle_id_five_m[-2]:
        new_candle = []
        start = True
        
    # Definir níveis de suporte e resistência
    support = min([i['close'] for i in candles])
    resistance = max([i['close'] for i in candles])

    if [i['close'] for i in candles][-1] < sma and [i['close'] for i in candles][-1] <= support + threshold and start:

        print(f"Compra detectada!")
        print(f'tentativa de compra R$ {format_currency(value)}')
        status, status_check, wins, loss = API.call_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=payoff, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        
        if status_check == 'win':
            value = float(format(API.balance(account_type) * 0.02, '.2f'))
            
            if API.balance(account_type) >= goal:
                print('meta batida')
                exit()
            
            if value < 2:
                value = 2
                
            if value > 20000:
                value = 20000
                
        if len(loss) > 0 and status_check == 'loose':
            value = API.martingale(value, len(loss))
            
            if value > API.balance(account_type):
                print('stop loss acionado')
                exit()
            
            if value < 2:
                value = 2
        
            if value > 20000:
                value = 20000
            
            if API.balance(account_type) >= goal:
                print('meta batida')
                exit()

    # Se estiver acima, verificar se o preço chegou ao nível de resistência
    elif [i['close'] for i in candles][-1] > sma and [i['close'] for i in candles][-1] >= resistance - threshold and start:

        print(f"Venda detectada!")
        print(f'tentativa de venda R$ {format_currency(value)}')
        status, status_check, wins, loss = API.put_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=payoff, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        
        if status_check == 'win':
            value = float(format(API.balance(account_type) * 0.02, '.2f'))
            
            if API.balance(account_type) >= goal:
                print('meta batida')
                exit()
            
            if value < 2:
                value = 2
            
            if value > 20000:
                value = 20000
            
        if len(loss) > 0 and status_check == 'loose':
            value = API.martingale(value, len(loss))
            
            if API.balance(account_type) >= goal:
                print('meta batida')
                exit()
            
            if value > API.balance(account_type):
                print('stop loss acionado')
                exit()
            
            if value < 2:
                value = 2
        
            if value > 20000:
                value = 20000
    else:
        active = API.change_active(mkt, otc)
        historic_five_minutes = API.get_realtime_candles(
            active, 300, total_candles_df)
        historic_five_minutes = [{'candle': 'red' if historic_five_minutes[i]['open'] > historic_five_minutes[i]['close']
                                    else 'green' if historic_five_minutes[i]['close'] > historic_five_minutes[i]['open'] else 'dogi',
                                    'close': historic_five_minutes[i]['close'], 'open': historic_five_minutes[i]['open'],
                                    'max': historic_five_minutes[i]['max'], 'min': historic_five_minutes[i]['min'], 'id': historic_five_minutes[i]['id']}
                                    for i in historic_five_minutes]
        candles = API.get_all_candles(active, 300, total_candles_df)

    API.set_time_sleep(1)