# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from components.helpers import *
import datetime
import numpy as np
import getpass
from itertools import cycle

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
value_stop_loss = float(format(API.calculate_stop_loss(
    last_register_balance[0], stop_loss_rate[0]), '.2f'))

if value_stop_loss <= 0:
    print('margem de stop loss inválida')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)

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
    
try:
    trend_variation_percent = int(input('qual será a variação percentual da tendência: '))
except ValueError:
    print('valor inválido da variação percewntual da tenência')
    exit()

active_type = 'turbo'
active = API.get_all_actives()[active_index]

total_candles_df = 15
threshold = 0.001
current_hour = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

if mkt:
    active_index = [1, 2, 3, 4, 5, 6, 99, 101]
    index_iter = cycle(active_index)

if otc:
    active_index = [76, 77, 78, 79, 80, 81, 84, 85, 86]
    index_iter = cycle(active_index)

wins = []
loss = []

print(f'horas: {current_hour.strftime("%H:%M:%S")}')
print(f'tipo de conta: {account_type}')
print(f'capital: {format_currency(balance)}')
print(f'meta do dia: {format_currency(goal)}')
print(f'stop loss: {format_currency(value_stop_loss)}')
print(f'ativo: {active}')
print(f'payoff: {API.get_profit(active, active_type) * 100}%')
print(f'gerenciamento: {goal_win}X{goal_loss}')
print('processando algoritmo')

while True:
    
    start = False
    candles = API.get_all_candles(active, 300, total_candles_df)
    profit = API.get_profit(active, active_type)

    # Obtém a hora atual em Brasília
    current_hour = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=-3)))
    
    if current_hour.minute % 5 == 0:
        start = True

    # Preços de fechamento dos ativos
    prices = np.array([candle['close'] for candle in candles]).astype(float)
    value = float(format(API.balance(account_type) * 0.01, '.2f'))
    
    # Reajuste no preço de entrada
    value = 2 if value < 2 else 20000 if value > 20000 else value

    # Variação percentual dos preços do ativo para calculo da tendencia
    percent_change = [((prices[i] - prices[i - 1]) / prices[i - 1])
                      * 100 for i in range(1, len(prices))]

    upward_trend = [change > 0 for change in percent_change]
    downward_trend = [change < 0 for change in percent_change]

    # Tendencia atual do mercado ingrime
    downward_trend = float(
        format((downward_trend.count(True) / len(downward_trend)) * 100, '.2f'))
    upward_trend = float(
        format((upward_trend.count(True) / len(upward_trend)) * 100, '.2f'))

    # Calculo para definir um candle de força
    prices_open = np.array([candle['open'] for candle in candles]).astype(float)
    candle_force = float(
        format((prices[-1] - prices_open[-1]) / prices_open[-1], '.2f'))

    # Definir níveis de suporte e resistência
    support = min(prices)
    resistance = max(prices)

    # Calculo do valor estocástico
    k = 100 * (prices[-1] - support) / (resistance - support)

    if API.balance(account_type) >= goal:
        print('meta batida')
        exit()

    if API.balance(account_type) <= value_stop_loss:
        print('stop loss acionado')
        exit()

    if value > API.balance(account_type):
        print('stop loss acionado')
        exit()
    
    # Verificação de um candle de força compradora
    if candle_force >= 0.24:

        print(
            f'Tentativa de venda Candle de Força {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}')
        status, status_check, wins, loss = API.put_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=profit, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        API.set_time_sleep(400)

    # Verificação de um candle de força vendedora
    elif candle_force <= -0.24:

        print(
            f'Tentativa de compra Candle de Força {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}')
        status, status_check, wins, loss = API.call_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=profit, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        API.set_time_sleep(400)

    # Verificação estocastico força alta compradora
    elif k > 80 and upward_trend > trend_variation_percent and start:

        print(
            f'Tentativa de venda Estocastico {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}, tendência de alta: {upward_trend}%')
        status, status_check, wins, loss = API.put_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=profit, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        API.set_time_sleep(400)

    # Verificação estocastico força alta vendedora
    elif k < 20 and downward_trend > trend_variation_percent and start:

        print(
            f'Tentativa de compra Estocastico {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}, tendência de baixa: {downward_trend}%')
        status, status_check, wins, loss = API.call_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=profit, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        API.set_time_sleep(400)

    # Verificação pullback em tendência de alta
    elif prices[-1] <= support + threshold and upward_trend > trend_variation_percent and start:

        print(
            f'Tentativa de compra Pullback {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}, tendência de alta: {upward_trend}%')
        status, status_check, wins, loss = API.call_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=profit, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        API.set_time_sleep(400)

    # Verificação pullback em tendência de baixa
    elif prices[-1] >= resistance - threshold and downward_trend > trend_variation_percent and start:

        print(
            f'Tentativa de venda Pullback {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}, tendência de baixa: {downward_trend}%')
        status, status_check, wins, loss = API.put_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=profit, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        API.set_time_sleep(400)
        
    else:
        active = API.change_active(index_iter)

    API.set_time_sleep(1)
