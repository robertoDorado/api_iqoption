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

threshold = 0.001
current_hour = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

if mkt:
    active_index = [1, 2, 3, 4, 5, 6, 99, 101]
    index_iter = cycle(active_index)

if otc:
    active_index = [76, 77, 79, 81, 84, 85, 1381, 1380, 1382]
    index_iter = cycle(active_index)

wins = []
loss = []

limiar_volatility = 0.05

print(f'horas: {current_hour.strftime("%H:%M:%S")}')
print(f'tipo de conta: {account_type}')
print(f'capital: {format_currency(balance)}')
print(f'ativo: {active}')
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

    # Calculo da média dos preços
    sma = np.mean(prices)

    # Calcular o retorno dos preços em variação percentual
    returns_variation_percent = np.diff(prices) / prices[:-1]

    # Calculo do desvio padrão
    std = np.std(returns_variation_percent)

    # Calculo de 1% do valor de entrada
    value = float(format(API.balance(account_type) * 0.01, '.2f'))

    # Calculo da distribuição normal para projetar o preço atual do ativo
    current_price_probability_high = API.normal_distribution(sma, std, prices[-1], 'High') * 100
    current_price_probability_low = API.normal_distribution(sma, std, prices[-1], 'Low') * 100

    # Calculo da volatilidade usando o desvio padrão
    volatility_price = float(
        format(std * np.sqrt(252), '.2f'))

    # Verificar se o ativo está com os preços voláteis
    if volatility_price >= limiar_volatility:
        continue

    # Reajuste no preço de entrada
    value = 2 if value < 2 else 20000 if value > 20000 else value

    # Variação percentual dos preços do ativo para calculo da tendencia
    percent_change = [((prices[i] - prices[i - 1]) / prices[i - 1])
                      * 100 for i in range(1, len(prices))]

    # Desvio padrão da tendência
    trend_std = np.std(percent_change)
    
    # Média da tendência
    trend_sma = np.mean(percent_change) * 100
    
    # Total da minha amostra
    n = len(percent_change)
    
    # Calculo da margem de erro com 95% de nivel de confiança
    margin_of_error = 1.96 * (trend_std / np.sqrt(n))
    
    # definindo a tendência minima de confiança
    trend_minium = trend_sma - margin_of_error

    # Definir níveis de suporte e resistência
    support = min(prices)
    resistance = max(prices)

    # Calculo do valor estocástico
    k = 100 * (prices[-1] - support) / (resistance - support)

    if value > API.balance(account_type):
        print('stop loss acionado')
        exit()

    print(f'Ativo: {active}')
    print(f'Estocastico: {k}%')
    print(f'Media da tendência: {trend_sma}%')
    print(f'Minima da tendência: {trend_minium}%')
    print(f'Probabilidade do preço em alta: {current_price_probability_high}%')
    print(f'Probabilidade do preço em baixa: {current_price_probability_low}%')
    print(f'-----------------')
    
    active = API.change_active(index_iter)
    API.set_time_sleep(1)
