# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from datetime import datetime
import numpy as np
from components.helpers import *
import getpass

try:
    grow_rate = get_grow_rate()
    stop_loss_rate = get_stop_loss_rate()
    initial_capital = get_initial_capital()
except:
    print('tabela meta mês está vazia ou mal configurada')
    exit()

if count_registers()[0] > 0:
    i = 1
    last_register_balance = get_first_register_balance(i)
    while last_register_balance == None:
        i += 1
        last_register_balance = get_first_register_balance(i)
else:
    last_register_balance = (initial_capital[0],)

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
    
goal = float(format(API.calculate_goal(last_register_balance[0], grow_rate[0]), '.2f'))
value_stop_loss = float(format(API.calculate_stop_loss(last_register_balance[0], stop_loss_rate[0]), '.2f'))

if value_stop_loss <= 0:
    print('margem de stop loss inválida')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)

total_candles = 50

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

value = float(format(API.balance(account_type) * 0.01, '.2f'))
value = 2 if value < 2 else 20000 if value > 20000 else value

total_candles_df = total_candles
new_candle = []

time = datetime.now()
hour = time.hour
minute = time.minute
second = time.second

threshold = 0.5

hours = f'0{hour}' if hour < 10 else hour
minutes = f'0{minute}' if minute < 10 else minute
seconds = f'0{second}' if second < 10 else second

wins = []
loss = []

print(f'horas: {hours}:{minutes}:{seconds}')
print(f'tipo de conta: {account_type}')
print(f'capital: {format_currency(balance)}')
print(f'meta do dia: {format_currency(goal)}')
print(f'stop loss: {format_currency(value_stop_loss)}')
print(f'primeiro valor de entrada: {format_currency(value)}')
print(f'ativo: {active}')
print(f'payoff: {payoff}%')
print(f'gerenciamento: {goal_win}X{goal_loss}')
print('processando algoritmo')

while True:

    start = False
    
    history_five_minutes = API.get_realtime_candles(active, 300, total_candles_df)
    history_five_minutes = [{'id': history_five_minutes[i]['id']} for i in history_five_minutes]
    candles = API.get_all_candles(active, 300, total_candles_df)

    # calcular a média móvel simples (SMA) dos últimos n períodos
    prices = np.array([candle['close'] for candle in candles]).astype(float)
    sma = np.mean(prices)

    all_candle_id_five_m = [i['id'] for i in history_five_minutes]

    if len(new_candle) < 1:
        new_candle.append(all_candle_id_five_m[-1])

    if new_candle[0] == all_candle_id_five_m[-2]:
        new_candle = []
        start = True

    # Definir níveis de suporte e resistência
    support = min([i['close'] for i in candles])
    resistance = max([i['close'] for i in candles])

    if API.balance(account_type) >= goal:
        print('meta batida')
        exit()

    if API.balance(account_type) <= value_stop_loss:
        print('stop loss acionado')
        exit()

    if value > API.balance(account_type):
        print('stop loss acionado')
        exit()

    value = 2 if value < 2 else 20000 if value > 20000 else value
    # Se estiver abaixo, verificar se o preço chegou ao nível de suporte
    if [i['close'] for i in candles][-1] < sma and [i['close'] for i in candles][-1] <= support + threshold and start:

        print(f"Compra detectada!")
        print(f'tentativa de compra {format_currency(value)}')
        status, status_check, wins, loss = API.call_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=payoff, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        
        if status_check == 'loose':
            value = float(format(API.balance(account_type) * 0.01, '.2f'))
        elif status_check == 'win' and len(wins) > 0:
            value = API.soros(value, len(wins))
            
    # Se estiver acima, verificar se o preço chegou ao nível de resistência
    elif [i['close'] for i in candles][-1] > sma and [i['close'] for i in candles][-1] >= resistance - threshold and start:

        print(f"Venda detectada!")
        print(f'tentativa de venda {format_currency(value)}')
        status, status_check, wins, loss = API.put_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=payoff, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        
        if status_check == 'loose':
            value = float(format(API.balance(account_type) * 0.01, '.2f'))
        elif status_check == 'win' and len(wins) > 0:
            value = API.soros(value, len(wins))
        
    else:
        active = API.change_active(mkt, otc)
        history_five_minutes = API.get_realtime_candles(active, 300, total_candles_df)
        history_five_minutes = [{'id': history_five_minutes[i]['id']} for i in history_five_minutes]
        candles = API.get_all_candles(active, 300, total_candles_df)

    API.set_time_sleep(1)