# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option
from datetime import datetime
import numpy as np
from components.helpers import *

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

goal_win = 2
goal_loss = 1
    
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

total_registers = count_registers(account_type)[0]
total_win = count_win_registers(account_type)[0]
total_loss = count_loss_registers(account_type)[0]

fishing = False

if total_registers == 0:
    total_registers = 2
    
if total_win == 0:
    total_win = 1

if total_loss >= 0:
    total_loss = 1

active_type = 'turbo'
active = API.get_all_actives()[active_index]
payoff = API.get_profit(active, active_type) * 100

if fishing == False:
    value = 2

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

print(f'minha conta e {account_type}: R$ {format_currency(balance)}, ativo: {active}, payoff de {payoff}%, horas: {hours}:{minutes}:{seconds}, gerenciamento: {goal_win}X{goal_loss}, entrada: R$ {format_currency(value)}')
print('iniciando algoritmo')

while True:

    start = False
    fishing = False

    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)

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

    all_candle_id_five_m = [i['id'] for i in historic_five_minutes]

    if len(new_candle) < 1:
        new_candle.append(all_candle_id_five_m[-1])

    if new_candle[0] == all_candle_id_five_m[-2]:
        new_candle = []
        start = True


    # tomada de decisão para mercado lateralizado
    # Verificar se o preço está perto da SMA
    if consolidated_market and mkt:
        
        if [i['open'] for i in candles][-1] < sma * 1.01 and [i['open'] for i in candles][-1] > sma * 0.99:
            
            # Aguardar a entrada
            API.set_time_sleep(15 * 60) # 15 minutos
        
        # Verificar se o preço não saiu do intervalo
        if [i['open'] for i in candles][-1] < sma * 1.01 and [i['open'] for i in candles][-1] > sma * 0.99:
            
            # Definir sentido da entrada
            if [i['open'] for i in candles][-1] < sma:
                
                print("mercado lateralizado, compra realizada")
                
                if value >= 20000:
                    value = 20000
                elif value < 2:
                    value = 2
                
                status, fishing = API.call_decision(value, active, wins, stop_loss, active_type, payoff, goal_win, goal_loss, account_type, fishing)
                
                if fishing:
                    balance = API.balance(account_type)
                    fraction = API.kelly(payoff, float(format(total_win / total_registers, '.2f')), float(format(total_loss / total_registers, '.2f')))
                    value = float(format(balance * fraction, '.2f'))
                else:
                    value = 2
                
                if value >= 20000:
                    print(f'proxima entrada: R$ 20.000,00')
                elif value < 2:
                    print(f'proxima entrada: R$ 2,00')
                else:
                    print(f'proxima entrada: R$ {format_currency(value)}')  
            else:
                print("mercado lateralizado, venda realizada")
            
                if value >= 20000:
                    value = 20000
                elif value < 2:
                    value = 2
                    
                status, fishing = API.put_decision(value, active, wins, stop_loss, active_type, payoff, goal_win, goal_loss, account_type, fishing)
                
                if fishing:
                    balance = API.balance(account_type)
                    fraction = API.kelly(payoff, float(format(total_win / total_registers, '.2f')), float(format(total_loss / total_registers, '.2f')))
                    value = float(format(balance * fraction, '.2f'))
                else:
                    value = 2
                
                if value >= 20000:
                    print(f'proxima entrada: R$ 20.000,00')
                elif value < 2:
                    print(f'proxima entrada: R$ 2,00')
                else:
                    print(f'proxima entrada: R$ {format_currency(value)}')
                    
    # tomada de decisão para mercado lateralizado na OTC
    elif consolidated_market and otc:
        # Verificar se o preço está perto da SMA
        if [i['open'] for i in candles][-1] < sma * 1.01 and [i['open'] for i in candles][-1] > sma * 0.99:
            
            # Aguardar a entrada
            API.set_time_sleep(15 * 60) # 15 minutos
        
        # Verificar se o preço não saiu do intervalo
        if [i['open'] for i in candles][-1] < sma * 1.01 and [i['open'] for i in candles][-1] > sma * 0.99:
            
            # Definir sentido da entrada
            if [i['open'] for i in candles][-1] < sma:
                
                print("mercado lateralizado, compra realizada na OTC")
                
                if value >= 20000:
                    value = 20000
                elif value < 2:
                    value = 2
                
                status, fishing = API.call_decision(value, active, wins, stop_loss, active_type, payoff, goal_win, goal_loss, account_type, fishing)
                
                if fishing:
                    balance = API.balance(account_type)
                    fraction = API.kelly(payoff, float(format(total_win / total_registers, '.2f')), float(format(total_loss / total_registers, '.2f')))
                    value = float(format(balance * fraction, '.2f'))
                else:
                    value = 2
                
                if value >= 20000:
                    print(f'proxima entrada: R$ 20.000,00')
                elif value < 2:
                    print(f'proxima entrada: R$ 2,00')
                else:
                    print(f'proxima entrada: R$ {format_currency(value)}')  
            else:
                print("mercado lateralizado, venda realizada na OTC")
            
                if value >= 20000:
                    value = 20000
                elif value < 2:
                    value = 2
                    
                status, fishing = API.put_decision(value, active, wins, stop_loss, active_type, payoff, goal_win, goal_loss, account_type, fishing)
                
                if fishing:
                    balance = API.balance(account_type)
                    fraction = API.kelly(payoff, float(format(total_win / total_registers, '.2f')), float(format(total_loss / total_registers, '.2f')))
                    value = float(format(balance * fraction, '.2f'))
                else:
                    value = 2
                
                if value >= 20000:
                    print(f'proxima entrada: R$ 20.000,00')
                elif value < 2:
                    print(f'proxima entrada: R$ 2,00')
                else:
                    print(f'proxima entrada: R$ {format_currency(value)}')
    
    
    # tomada decisão pullback no mkt caso contrario seria na otc
    # Verificar se o preço está abaixo da SMA
    # Se estiver abaixo, verificar se o preço chegou ao nível de suporte
    if mkt:
        
        # Definir níveis de suporte e resistência
        support = min([i['close'] for i in candles])
        resistance = max([i['close'] for i in candles])
        
        if [i['close'] for i in candles][-1] < sma and [i['close'] for i in candles][-1] <= support + threshold and start:
            
            print("Pullback de compra detectado!")
            
            if value >= 20000:
                value = 20000
            elif value < 2:
                value = 2
            
            status, fishing = API.call_decision(value, active, wins, stop_loss, active_type, payoff, goal_win, goal_loss, account_type, fishing)
            
            if fishing:
                balance = API.balance(account_type)
                fraction = API.kelly(payoff, float(format(total_win / total_registers, '.2f')), float(format(total_loss / total_registers, '.2f')))
                value = float(format(balance * fraction, '.2f'))
            else:
                value = 2
            
            if value >= 20000:
                print(f'proxima entrada: R$ 20.000,00')
            elif value < 2:
                print(f'proxima entrada: R$ 2,00')
            else:
                print(f'proxima entrada: R$ {format_currency(value)}')
                
            
        # Se estiver acima, verificar se o preço chegou ao nível de resistência
        elif [i['close'] for i in candles][-1] > sma and [i['close'] for i in candles][-1] >= resistance - threshold and start:
                
            print("Pullback de venda detectado!")
            
            if value >= 20000:
                value = 20000
            elif value < 2:
                value = 2
                
            status, fishing = API.put_decision(value, active, wins, stop_loss, active_type, payoff, goal_win, goal_loss, account_type, fishing)
            
            if fishing:
                balance = API.balance(account_type)
                fraction = API.kelly(payoff, float(format(total_win / total_registers, '.2f')), float(format(total_loss / total_registers, '.2f')))
                value = float(format(balance * fraction, '.2f'))
            else:
                value = 2
            
            if value >= 20000:
                print(f'proxima entrada: R$ 20.000,00')
            elif value < 2:
                print(f'proxima entrada: R$ 2,00')
            else:
                print(f'proxima entrada: R$ {format_currency(value)}')
    else:
        # estratégia de pullback para o mercado OTC
        max_value = max([i["max"] for i in candles][-2], [i["open"] for i in candles][-2])
        min_value = min([i["min"] for i in candles][-2], [i["open"] for i in candles][-2])
        
        # extrai os preços de abertura e fechamento dos dados do mercado
        precos = np.array([[candle["open"], candle["close"]] for candle in candles])
        
        # calcula o preço máximo e mínimo
        preco_maximo = np.max(precos)
        preco_minimo = np.min(precos)
        
        # calcula o valor do pullback
        pullback = preco_maximo - ((preco_maximo - preco_minimo) * 0.382)
        
        # verifica se o preço atual está abaixo do pullback
        preco_atual = precos[-1, 1]
        
        if [i['close'] for i in candles][-1] < min_value + threshold and preco_atual < pullback and preco_atual < sma and start:
            
            print("Pullback OTC de compra detectado!")
            
            if value >= 20000:
                value = 20000
            elif value < 2:
                value = 2
                
            status, fishing = API.call_decision(value, active, wins, stop_loss, active_type, payoff, goal_win, goal_loss, account_type, fishing)
            
            if fishing:
                balance = API.balance(account_type)
                fraction = API.kelly(payoff, float(format(total_win / total_registers, '.2f')), float(format(total_loss / total_registers, '.2f')))
                value = float(format(balance * fraction, '.2f'))
            else:
                value = 2
            
            if value >= 20000:
                print(f'proxima entrada: R$ 20.000,00')
            elif value < 2:
                print(f'proxima entrada: R$ 2,00')
            else:
                print(f'proxima entrada: R$ {format_currency(value)}')
                
        elif [i['close'] for i in candles][-1] > max_value - threshold and preco_atual > pullback and preco_atual > sma and start:

            print("Pullback OTC de venda detectado!")
            
            if value >= 20000:
                value = 20000
            elif value < 2:
                value = 2
                    
            status, fishing = API.put_decision(value, active, wins, stop_loss, active_type, payoff, goal_win, goal_loss, account_type, fishing)
            
            if fishing:
                balance = API.balance(account_type)
                fraction = API.kelly(payoff, float(format(total_win / total_registers, '.2f')), float(format(total_loss / total_registers, '.2f')))
                value = float(format(balance * fraction, '.2f'))
            else:
                value = 2
            
            if value >= 20000:
                print(f'proxima entrada: R$ 20.000,00')
            elif value < 2:
                print(f'proxima entrada: R$ 2,00')
            else:
                print(f'proxima entrada: R$ {format_currency(value)}')
        
    API.set_time_sleep(1)