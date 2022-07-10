# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from random import choices
from datetime import datetime

API = BOT_IQ_Option()

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

date = datetime.now()

actives = API.get_all_actives()

actives_code = [1, 3, 5]
actives_code_otc = [76, 77, 79]

value = 5

if date.weekday() == 5 or date.weekday() == 6:
    actives_code = choices(actives_code_otc)[0]
    print(f'iniciando a busca no ativo {actives[actives_code]}')
else:
    actives_code = choices(actives_code)[0]
    print(f'iniciando a busca no ativo {actives[actives_code]}')

profit = API.get_profit(actives[actives_code], 'turbo') * 100
balance = API.balance()

wins = []
loss = []

win_value = []
loss_value = []

red_analitics = []
green_analitics = []
i = 0

while True:

    try:
        
        i = i + 1
        
        if i == 10 or i == 20 or i == 30 or i == 40 or i == 50 or i == 60:
            if date.weekday() == 5 or date.weekday() == 6:
                actives_code = choices(actives_code_otc)[0]
                print(f'buscando em {actives[actives_code]}')
            else:
                actives_code = choices(actives_code)[0]
                print(f'buscando em {actives[actives_code]}')
        elif i > 60:
            print('mercado ruim para efetuar operações de trade')
            exit()
        
        candles = API.get_all_candles(actives[actives_code], 60, 12) # 62 velas para decisões de 5 minutos e 12 velas para 1 minuto

        candles = [{'close': i['close'], 'open': i['open'],
        'candle_color': 'red_candle' if i['open'] > i['close']
        else 'green_candle' if i['open'] < i['close'] else 'dogi'} for i in candles]

        red_candles = [x['candle_color']
            for x in candles if x['candle_color'] == 'red_candle']
        green_candles = [x['candle_color']
            for x in candles if x['candle_color'] == 'green_candle']
        
        total_candles = len(green_candles) + len(red_candles)
        percent_green = round(len(green_candles) / total_candles * 100)
        percent_red = round(len(red_candles) / total_candles * 100)
        
        if len(red_analitics) <= 3 and len(green_analitics) <= 3:
            
            red_analitics.append(percent_red)
            green_analitics.append(percent_green)
            
            if sum(green_analitics) > sum(red_analitics):
                critical_percent = sum(green_analitics) - sum(red_analitics)
            elif sum(green_analitics) < sum(red_analitics):
                critical_percent = sum(red_analitics) - sum(green_analitics)
                
            if green_analitics > red_analitics and critical_percent > 100:
                
                print(f'venda: {sum(green_analitics)}%')
                print(f'compra: {sum(red_analitics)}%')
                
                if balance > value:
                    status, id = API.call_or_put(value, actives[actives_code], 'put', 1)
                else:
                    print('saldo insuficiente')
                    exit()
                    
                print(f'venda realizada de: R$ {round(value, 2)}')
                
                if status:
                    status, check_value = API.check_win_or_loss(id, 'v4')
                    
                    if status == 'win':
                        wins.append(status)
                        win_value.append(check_value)
                        
                        print(f'total wins: {len(wins)}, R$ {round(sum(win_value), 2)}')
                    else:
                        loss.append(status)
                        loss_value.append(check_value)
                        
                        print(f'total loss: {len(loss)}, - R$ {round(sum(loss_value), 2) * - 1}')
            
            if red_analitics > green_analitics and critical_percent > 100:
                
                print(f'venda: {sum(green_analitics)}%')
                print(f'compra: {sum(red_analitics)}%')
                
                if balance > value:
                    status, id = API.call_or_put(value, actives[actives_code], 'call', 1)
                else:
                    print('saldo insuficiente')
                    exit()
                    
                print(f'compra realizada de: R$ {round(value, 2)}')
                
                if status:
                    status, check_value = API.check_win_or_loss(id, 'v4')
                    
                    if status == 'win':
                        wins.append(status)
                        win_value.append(check_value)
                        
                        print(f'total wins: {len(wins)}, R$ {round(sum(win_value), 2)}')
                    else:
                        loss.append(status)
                        loss_value.append(check_value)
                        
                        print(f'total loss: {len(loss)}, -R$ {round(sum(loss_value), 2) * - 1}')
                            
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')