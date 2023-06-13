# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from components.helpers import *
import datetime
import numpy as np
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

active_type = 'turbo'
active = API.get_all_actives()[active_index]

value = float(format(API.balance(account_type) * 0.02, '.2f'))
value = 2 if value < 2 else 20000 if value > 20000 else value

total_candles_df = 15
threshold = 0.001
current_hour = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

wins = []
loss = []

print(f'horas: {current_hour.strftime("%H:%M:%S")}')
print(f'tipo de conta: {account_type}')
print(f'capital: {format_currency(balance)}')
print(f'meta do dia: {format_currency(goal)}')
print(f'stop loss: {format_currency(value_stop_loss)}')
print(f'primeiro valor de entrada: {format_currency(value)}')
print(f'ativo: {active}')
print(f'payoff: {API.get_profit(active, active_type) * 100}%')
print(f'gerenciamento: {goal_win}X{goal_loss}')
print('processando algoritmo')

while True:

    candles = API.get_all_candles(active, 300, total_candles_df)

    # Obtém a hora atual em Brasília
    current_hour = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=-3)))

    # Calcular a média móvel simples (SMA) dos últimos n períodos
    prices = np.array([candle['close'] for candle in candles]).astype(float)
    sma = np.mean(prices)

    # Tendencia atual do mercado
    tendencie = "High" if prices[-1] > sma else "Low" if prices[-1] < sma else "Equal"

    # Variação percentual dos preços do ativo para calculo da tendencia
    percent_change = [((prices[i] - prices[-1]) / prices[-1])
                      * 100 for i in range(1, len(prices))]

    # Tendencia atual do mercado ingrime
    upward_trend = all(change > 0 for change in percent_change)
    downward_trend = all(change < 0 for change in percent_change)

    # Calculo para definir um candle de força
    prices_open = np.array([candle['open'] for candle in candles]).astype(float)
    candle_force = float(
        format((prices[-1] - prices_open[-1]) / prices_open[-1], '.6f'))

    # Definir níveis de suporte e resistência
    support = min(prices)
    resistance = max(prices)

    # Reajuste no preço de entrada
    value = 2 if value < 2 else 20000 if value > 20000 else value

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

    # Verifique os sinais de compra/venda estocastico
    if k > 80 and upward_trend:

        print(
            f'Tentativa de venda Estocastico {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}')
        status, status_check, wins, loss = API.put_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=API.get_profit(active, active_type) * 100, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)

        if status_check == 'loose':
            value = float(format(API.balance(account_type) * 0.02, '.2f'))
            print(f'proxima entrada no valor de: {format_currency(value)}')
            API.set_time_sleep(400)
        elif status_check == 'win' and len(wins) > 0:
            value = float(
                format(API.soros(value, API.get_profit(active, active_type)), '.2f'))
            print(f'proxima entrada no valor de: {format_currency(value)}')
            API.set_time_sleep(400)

    elif k < 20 and downward_trend:

        print(
            f'Tentativa de compra Estocastico {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}')
        status, status_check, wins, loss = API.call_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=API.get_profit(active, active_type) * 100, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)

        if status_check == 'loose':
            value = float(format(API.balance(account_type) * 0.02, '.2f'))
            print(f'proxima entrada no valor de: {format_currency(value)}')
            API.set_time_sleep(400)
        elif status_check == 'win' and len(wins) > 0:
            value = float(
                format(API.soros(value, API.get_profit(active, active_type)), '.2f'))
            print(f'proxima entrada no valor de: {format_currency(value)}')
            API.set_time_sleep(400)

    # Se estiver abaixo, verificar se o preço chegou ao nível de suporte pullback
    elif prices[-1] < sma and prices[-1] <= support + threshold and tendencie == "High":

        print(
            f'Tentativa de compra Pullback {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}')
        status, status_check, wins, loss = API.call_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=API.get_profit(active, active_type) * 100, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)

        if status_check == 'loose':
            value = float(format(API.balance(account_type) * 0.02, '.2f'))
            print(f'proxima entrada no valor de: {format_currency(value)}')
            API.set_time_sleep(400)
        elif status_check == 'win' and len(wins) > 0:
            value = float(
                format(API.soros(value, API.get_profit(active, active_type)), '.2f'))
            print(f'proxima entrada no valor de: {format_currency(value)}')
            API.set_time_sleep(400)

    # Se estiver acima, verificar se o preço chegou ao nível de resistência
    elif prices[-1] > sma and prices[-1] >= resistance - threshold and tendencie == "Low":

        print(
            f'Tentativa de venda Pullback {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}')
        status, status_check, wins, loss = API.put_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=API.get_profit(active, active_type) * 100, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)

        if status_check == 'loose':
            value = float(format(API.balance(account_type) * 0.02, '.2f'))
            print(f'proxima entrada no valor de: {format_currency(value)}')
            API.set_time_sleep(400)
        elif status_check == 'win' and len(wins) > 0:
            value = float(
                format(API.soros(value, API.get_profit(active, active_type)), '.2f'))
            print(f'proxima entrada no valor de: {format_currency(value)}')
            API.set_time_sleep(400)

    elif candle_force > 0.264964:

        value = float(format(API.balance(account_type) * 0.06, '.2f'))
        print(
            f'Tentativa de venda Candle de Força {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}')
        status, status_check, wins, loss = API.put_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=API.get_profit(active, active_type) * 100, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        API.set_time_sleep(400)

    elif candle_force < -0.264964:

        value = float(format(API.balance(account_type) * 0.06, '.2f'))
        print(
            f'Tentativa de compra Candle de Força {format_currency(value)}, ativo: {active}, horas: {current_hour.strftime("%H:%M:%S")}')
        status, status_check, wins, loss = API.call_decision(
            value=value, active=active, wins=wins, stop_loss=loss, payoff=API.get_profit(active, active_type) * 100, goal_win=goal_win, goal_loss=goal_loss, account_type=account_type)
        API.set_time_sleep(400)

    else:
        active = API.change_active(mkt, otc)
        candles = API.get_all_candles(active, 300, total_candles_df)

    API.set_time_sleep(1)
