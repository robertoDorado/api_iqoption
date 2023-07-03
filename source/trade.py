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

try:
    total_candles_df = int(input('qual será o total de candles para análise: '))
except ValueError:
    print('definição de gráfico inválido')
    exit()

try:
    timestamp_candle = int(input('qual será o timestamp da vela: '))
except ValueError:
    print('timestamp candle inválido')
    exit()

threshold = 0.001
current_hour = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

if mkt:
    active_index = [1, 2, 3, 4, 5, 6, 99, 101]
    index_iter = cycle(active_index)

if otc:
    active_index = [76, 77, 79, 81, 84, 85, 1381, 1380, 1382]
    index_iter = cycle(active_index)

limiar_volatility = 1

print(f'horas: {current_hour.strftime("%H:%M:%S")}')
print(f'tipo de conta: {account_type}')
print(f'capital: {format_currency(balance)}')
print(f'meta do dia: {format_currency(goal)}')
print(f'stop loss: {format_currency(value_stop_loss)}')
print(f'ativo: {active}')
print(f'payoff: {API.get_profit(active, active_type) * 100}%')
print('processando algoritmo')

while True:

    start = False

    candles = API.get_realtime_candles(active, 300, total_candles_df)
    profit = API.get_profit(active, active_type)

    # Obtém a hora atual em Brasília
    current_hour = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=-3)))

    # Obtém o horário da corretora
    borker_time = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=-3, minutes=-1, seconds=34)))

    if borker_time.minute % 5 == 0:
        start = True

    # Preços de fechamento dos ativos
    prices = np.array([candle['close'] for candle in candles]).astype(float)

    # Variação percentual dos preços do ativo para calculo da tendencia
    percent_change = [((prices[i] - prices[i - 1]) / prices[i - 1])
                      * 100 for i in range(1, len(prices))]

    # Teste Shapiro-Wilk para verificar se os dados da amostra estão normalizados
    statistics, pvalue = API.shap(percent_change)

    # Caso o pvalue seja maior que 0.05 a hipotese nula é rejeitada
    if pvalue < 0.05:
        active, current_index = API.change_active(index_iter)
        continue

    # Desvio padrão dos preços
    std = np.std(percent_change)

    # Média dos preços
    sma = np.mean(percent_change)

    # Calculo da distribuição normal para projetar o preço atual do ativo
    current_price_probability_high = API.normal_distribution(
        sma, std, percent_change[-1], 'High') * 100
    current_price_probability_low = API.normal_distribution(
        sma, std, percent_change[-1], 'Low') * 100

    # Calculo da volatilidade usando o desvio padrão
    volatility_price = float(
        format(std * np.sqrt(252), '.2f'))

    # Verificar se o ativo está com os preços voláteis
    if volatility_price >= limiar_volatility:
        active, current_index = API.change_active(index_iter)
        continue

    # Verifica se a variavel current_index existe no escopo local
    if 'current_index' not in locals():
        current_index = 1

    # Definir níveis de suporte e resistência
    support = min(percent_change)
    resistance = max(percent_change)

    # Calculo do valor estocástico
    k = 100 * (percent_change[-1] - support) / (resistance - support)

    if API.balance(account_type) >= goal:
        print('meta batida')
        exit()
        
    if API.balance(account_type) <= value_stop_loss:
        print('stop loss acionado')
        exit()

    print(f'Ativo: {active}')
    print(f'Estocastico: {k}%')
    print(f'Media da tendência: {sma}%')
    print(f'Probabilidade do preço em alta: {current_price_probability_high}%')
    print(f'Probabilidade do preço em baixa: {current_price_probability_low}%')
    print(f'-----------------')

    # Verificação estocastico força alta compradora
    if k > 40 and k < 50 and current_price_probability_high > 50 and sma > 0 and start:

        value = API.probability_on_input(current_price_probability_high, account_type)
        value = 2 if value < 2 else 20000 if value > 20000 else value
        print("############################")
        print(f'Tentativa de compra Estocastico {format_currency(value)}')
        print(f'Ativo: {active}')
        print(f'Horas: {current_hour.strftime("%H:%M:%S")}')
        print(f'Tendência de alta: {sma}%')
        print(f'Horas na corretora: {borker_time.strftime("%H:%M:%S")}')
        print(f'Probabilidade de preço atual em alta: {current_price_probability_high}%')
        status, status_check, active, current_index, index_iter = API.call_decision(
            index_iter=index_iter, current_index=current_index, active_index=active_index, value=value, active=active, payoff=profit, account_type=account_type, timestamp=timestamp_candle)
        print("############################")

        if status == False:
            active, current_index = API.change_active(index_iter)

    # Verificação estocastico força alta vendedora
    elif k > 50 and k < 65 and current_price_probability_low > 50 and sma < 0 and start:

        value = API.probability_on_input(current_price_probability_low, account_type)
        value = 2 if value < 2 else 20000 if value > 20000 else value
        print("############################")
        print(f'Tentativa de venda Estocastico {format_currency(value)}')
        print(f'Ativo: {active}')
        print(f'Horas: {current_hour.strftime("%H:%M:%S")}')
        print(f'Tendência de baixa: {sma}%')
        print(f'Horas na corretora: {borker_time.strftime("%H:%M:%S")}')
        print(f'Probabilidade de preço atual em baixa: {current_price_probability_low}%')
        status, status_check, active, current_index, index_iter = API.put_decision(
            index_iter=index_iter, current_index=current_index, active_index=active_index, value=value, active=active, payoff=profit, account_type=account_type, timestamp=timestamp_candle)
        print("############################")

        if status == False:
            active, current_index = API.change_active(index_iter)

    # Verificação pullback em tendência de alta
    elif percent_change[-1] <= support + threshold and current_price_probability_high > 50 and sma > 0 and start:

        value = API.probability_on_input(current_price_probability_high, account_type)
        value = 2 if value < 2 else 20000 if value > 20000 else value
        print("############################")
        print(f'Tentativa de compra Pullback {format_currency(value)}')
        print(f'Ativo: {active}')
        print(f'Horas: {current_hour.strftime("%H:%M:%S")}')
        print(f'Tendência de alta: {sma}%')
        print(f'Horas na Corretora: {borker_time.strftime("%H:%M:%S")}')
        print(f'Probabilidade de preço atual em alta: {current_price_probability_high}%')
        status, status_check, active, current_index, index_iter = API.call_decision(
            index_iter=index_iter, current_index=current_index, active_index=active_index, value=value, active=active, payoff=profit, account_type=account_type, timestamp=timestamp_candle)
        print("############################")

        if status == False:
            active, current_index = API.change_active(index_iter)

    # Verificação pullback em tendência de baixa
    elif percent_change[-1] >= resistance - threshold and current_price_probability_low > 50 and sma < 0 and start:

        value = API.probability_on_input(current_price_probability_low, account_type)
        value = 2 if value < 2 else 20000 if value > 20000 else value
        print("############################")
        print(f'Tentativa de venda Pullback {format_currency(value)}')
        print(f'Ativo: {active}')
        print(f'horas: {current_hour.strftime("%H:%M:%S")}')
        print(f'Tendência de baixa: {sma}%')
        print(f'Horas na corretora: {borker_time.strftime("%H:%M:%S")}')
        print(f'Probabilidade de preço atual em baixa: {current_price_probability_low}%')
        status, status_check, active, current_index, index_iter = API.put_decision(
            current_index=index_iter, active_index=active_index, value=value, active=active, payoff=profit, account_type=account_type, timestamp=timestamp_candle)
        print("############################")

        if status == False:
            active, current_index = API.change_active(index_iter)

    else:
        active, current_index = API.change_active(index_iter)

    API.set_time_sleep(1)
