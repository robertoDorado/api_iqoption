# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from components.helpers import *
import datetime
import numpy as np
from itertools import cycle
import logging
import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

email_iqoption = config['DEFAULT']['user']
password_iqoption = config['DEFAULT']['password']
account_type = config['DEFAULT']['account_type']

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

balance = API.balance(account_type)

try:
    goal = float(format(API.calculate_goal(balance, float(config['DEFAULT']['goal'])), '.2f'))
    value_stop_loss = float(format(API.calculate_stop_loss(balance, float(config['DEFAULT']['stop_loss'])), '.2f'))
except Exception as e:
    print('Definições de metas inválidas')
    exit()

if value_stop_loss <= 0:
    print('margem de stop loss inválida')
    exit()

market = config['DEFAULT']['market']
mkt = True if market == 'mkt' else False
otc = True if market == 'otc' else False

if mkt == False and otc == False:
    print('tipo de mercado inválido')
    exit()

active_type = config['DEFAULT']['active_type']
actives_open = API.get_instance().get_all_open_time()

actives_open = [active for active, info in actives_open[active_type].items() if info['open'] == True]
actives_open = list(map(lambda x: x.replace("-op", ""), actives_open))

active = API.get_all_actives()
active = {k: v for k, v in active.items() if v in actives_open}

otc_active = {k: v.upper() for k, v in active.items() if v.lower().endswith("-otc")}
mkt_active = {k: v.upper() for k, v in active.items() if v.lower().endswith("-otc") == False}

otc_active = list(otc_active.keys())
mkt_active = list(mkt_active.keys())

if len(mkt_active) == 0 and mkt:
    print('mercado-comum encerrado')
    exit()
    
if len(otc_active) == 0 and otc:
    print('mercado-otc encerrado')
    exit()
    
try:
    total_candles_df = int(config['DEFAULT']['total_candles'])
except ValueError:
    print('definição de gráfico inválido')
    exit()

try:
    timestamp_candle = int(config['DEFAULT']['timestamp_candles'])
except ValueError:
    print('timestamp candle inválido')
    exit()

threshold = 0.001
current_hour = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

if mkt:
    active_index = mkt_active
    index_iter = cycle(active_index)
    current_index = active_index[0]

if otc:
    active_index = otc_active
    index_iter = cycle(active_index)
    current_index = active_index[0]

active = active[current_index]
directory = os.path.dirname(os.path.abspath(__file__))
file_name = "log.txt"
real_path = os.path.join(directory, file_name)

logging.basicConfig(filename=real_path, level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    payoff = API.get_profit(active, active_type)
except Exception as e:
    print('Tipo de ativo inválido')
    exit()

print(f'horas: {current_hour.strftime("%H:%M:%S")}')
print(f'tipo de conta: {account_type}')
print(f'capital: {format_currency(balance)}')
print(f'meta do dia: {format_currency(goal)}')
print(f'stop loss: {format_currency(value_stop_loss)}')
print(f'ativo: {active}')
print(f'payoff: {payoff}%')
print('processando algoritmo')

wins = []
loss = []

try:
    while True:

        candles = API.get_realtime_candles(active, 300, total_candles_df)
        payoff = API.get_profit(active, active_type)

        # Obtém a hora atual em Brasília
        current_hour = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=-3)))

        # Obtém o horário da corretora
        borker_time = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=-3, minutes=-1, seconds=34)))

        # Preços de fechamento dos ativos
        prices = np.array([candle['close'] for candle in candles]).astype(float)

        # Variação percentual dos preços do ativo para calculo da tendencia
        percent_change = [((prices[i] - prices[i - 1]) / prices[i - 1])
                          * 100 for i in range(1, len(prices))]

        # Teste Shapiro-Wilk para verificar se os dados da amostra estão normalizados
        statistics, pvalue = API.shap(percent_change)
        
        # Caso o pvalue seja maior que 0.05 a hipotese nula é rejeitada
        if float(format(pvalue, '.2f')) < 0.05:
            active, current_index = API.change_active(index_iter, active_type)
            payoff = API.get_profit(active, active_type)
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
        print(f'Índice Shapiro: {pvalue}%')
        print(f'Payoff: {payoff}%')
        print(f'Volatilidade: {volatility_price}%')
        print(f'-----------------')

        # Verificação estocastico força alta compradora
        if k > 50 and k < 55 and current_price_probability_high > 50 and sma > 0:
            value = API.probability_on_input(current_price_probability_high, account_type)
            value = 2 if value < 2 else 20000 if value > 20000 else value

            status, status_check, active, current_index, index_iter, wins, loss = API.call_decision(
                index_iter=index_iter, current_index=current_index, active_index=active_index,
                value=value, active=active, account_type=account_type,
                timestamp=timestamp_candle, wins=wins, loss=loss)
            
            print("############################")
            print(f'Tentativa de compra Estocastico {format_currency(value)}')
            print(f'Ativo: {active}')
            print(f'Horas: {current_hour.strftime("%d/%m/%Y %H:%M:%S")}')
            print(f'Tendência de alta: {sma}%')
            print(f'Horas na corretora: {borker_time.strftime("%d/%m/%Y %H:%M:%S")}')
            print(f'Índice Shapiro: {pvalue}%')
            print(f'Volatilidade: {volatility_price}%')
            print(f'Probabilidade de preço atual em alta: {current_price_probability_high}%')
            print("############################")

            with open("source/trade.txt", "a") as file:
                file.write("############################\n")
                file.write(f'Tentativa de compra Estocastico {format_currency(value)}\n')
                file.write(f'Ativo: {active}\n')
                file.write(f'Horas: {current_hour.strftime("%d/%m/%Y %H:%M:%S")}\n')
                file.write(f'Tendência de alta: {sma}%\n')
                file.write(f'Horas na corretora: {borker_time.strftime("%d/%m/%Y %H:%M:%S")}\n')
                file.write(f'Índice Shapiro: {pvalue}%\n')
                file.write(f'Volatilidade: {volatility_price}%\n')
                file.write(f'Probabilidade de preço atual em alta: {current_price_probability_high}%\n')
                file.write(f'status: {status_check}\n')
                file.write("############################\n")
                file.close()

            if status == False:
                active, current_index = API.change_active(index_iter, active_type)
                payoff = API.get_profit(active, active_type)

        # Verificação estocastico força alta vendedora
        elif k > 55 and k < 60 and current_price_probability_low > 50 and sma < 0:
            value = API.probability_on_input(
                current_price_probability_low, account_type)
            value = 2 if value < 2 else 20000 if value > 20000 else value

            status, status_check, active, current_index, index_iter, wins, loss = API.put_decision(
                index_iter=index_iter, current_index=current_index, active_index=active_index,
                value=value, active=active, account_type=account_type,
                timestamp=timestamp_candle, wins=wins, loss=loss)
            
            print("############################")
            print(f'Tentativa de venda Estocastico {format_currency(value)}')
            print(f'Ativo: {active}')
            print(f'Horas: {current_hour.strftime("%d/%m/%Y %H:%M:%S")}')
            print(f'Tendência de baixa: {sma}%')
            print(f'Horas na corretora: {borker_time.strftime("%d/%m/%Y %H:%M:%S")}')
            print(f'Índice Shapiro: {pvalue}%')
            print(f'Volatilidade: {volatility_price}%')
            print(f'Probabilidade de preço atual em baixa: {current_price_probability_low}%')
            print("############################")

            with open("source/trade.txt", "a") as file:
                file.write("############################\n")
                file.write(f'Tentativa de venda Estocastico {format_currency(value)}\n')
                file.write(f'Ativo: {active}\n')
                file.write(f'Horas: {current_hour.strftime("%d/%m/%Y %H:%M:%S")}\n')
                file.write(f'Tendência de baixa: {sma}%\n')
                file.write(f'Horas na corretora: {borker_time.strftime("%d/%m/%Y %H:%M:%S")}\n')
                file.write(f'Índice Shapiro: {pvalue}%\n')
                file.write(f'Volatilidade: {volatility_price}%\n')
                file.write(f'Probabilidade de preço atual em baixa: {current_price_probability_low}%\n')
                file.write(f'status: {status_check}\n')
                file.write("############################\n")
                file.close()

            if status == False:
                active, current_index = API.change_active(index_iter, active_type)
                payoff = API.get_profit(active, active_type)

        # Verificação pullback em tendência de alta
        elif percent_change[-1] <= support + threshold and current_price_probability_high > 50 and sma > 0:
            value = API.probability_on_input(current_price_probability_high, account_type)
            value = 2 if value < 2 else 20000 if value > 20000 else value

            status, status_check, active, current_index, index_iter, wins, loss = API.call_decision(
                index_iter=index_iter, current_index=current_index, active_index=active_index,
                value=value, active=active, account_type=account_type,
                timestamp=timestamp_candle, wins=wins, loss=loss)
            
            print("############################")
            print(f'Tentativa de compra Pullback {format_currency(value)}')
            print(f'Ativo: {active}')
            print(f'Horas: {current_hour.strftime("%d/%m/%Y %H:%M:%S")}')
            print(f'Tendência de alta: {sma}%')
            print(f'Horas na Corretora: {borker_time.strftime("%d/%m/%Y %H:%M:%S")}')
            print(f'Índice Shapiro: {pvalue}%')
            print(f'Volatilidade: {volatility_price}%')
            print(f'Probabilidade de preço atual em alta: {current_price_probability_high}%')
            print("############################")

            with open("source/trade.txt", "a") as file:
                file.write("############################\n")
                file.write(f'Tentativa de compra Pullback {format_currency(value)}\n')
                file.write(f'Ativo: {active}\n')
                file.write(f'Horas: {current_hour.strftime("%d/%m/%Y %H:%M:%S")}\n')
                file.write(f'Tendência de alta: {sma}%\n')
                file.write(f'Horas na Corretora: {borker_time.strftime("%d/%m/%Y %H:%M:%S")}\n')
                file.write(f'Índice Shapiro: {pvalue}%\n')
                file.write(f'Volatilidade: {volatility_price}%\n')
                file.write(f'Probabilidade de preço atual em alta: {current_price_probability_high}%\n')
                file.write(f'status: {status_check}\n')
                file.write("############################\n")
                file.close()

            if status == False:
                active, current_index = API.change_active(index_iter, active_type)
                payoff = API.get_profit(active, active_type)

        # Verificação pullback em tendência de baixa
        elif percent_change[-1] >= resistance - threshold and current_price_probability_low > 50 and sma < 0:
            value = API.probability_on_input(current_price_probability_low, account_type)
            value = 2 if value < 2 else 20000 if value > 20000 else value
            
            status, status_check, active, current_index, index_iter, wins, loss = API.put_decision(
                current_index=index_iter, active_index=active_index, value=value, active=active,
                account_type=account_type, timestamp=timestamp_candle, wins=wins, loss=loss)
            
            print("############################")
            print(f'Tentativa de venda Pullback {format_currency(value)}')
            print(f'Ativo: {active}')
            print(f'horas: {current_hour.strftime("%d/%m/%Y %H:%M:%S")}')
            print(f'Tendência de baixa: {sma}%')
            print(f'Horas na corretora: {borker_time.strftime("%d/%m/%Y %H:%M:%S")}')
            print(f'Índice Shapiro: {pvalue}%')
            print(f'Volatilidade: {volatility_price}%')
            print(f'Probabilidade de preço atual em baixa: {current_price_probability_low}%')
            print("############################")

            with open("source/trade.txt", "a") as file:
                file.write("############################\n")
                file.write(f'Tentativa de venda Pullback {format_currency(value)}\n')
                file.write(f'Ativo: {active}\n')
                file.write(f'horas: {current_hour.strftime("%d/%m/%Y %H:%M:%S")}\n')
                file.write(f'Tendência de baixa: {sma}%\n')
                file.write(f'Horas na corretora: {borker_time.strftime("%d/%m/%Y %H:%M:%S")}\n')
                file.write(f'Índice Shapiro: {pvalue}%\n')
                file.write(f'Volatilidade: {volatility_price}%\n')
                file.write(f'Probabilidade de preço atual em baixa: {current_price_probability_low}%\n')
                file.write(f'status: {status_check}\n')
                file.write("############################\n")
                file.close()

            if status == False:
                active, current_index = API.change_active(index_iter, active_type)
                payoff = API.get_profit(active, active_type)

        else:
            active, current_index = API.change_active(index_iter, active_type)
            payoff = API.get_profit(active, active_type)

        API.set_time_sleep(1)
except Exception as e:
    # Registra a mensagem de erro no arquivo de log
    logging.error(str(e))
