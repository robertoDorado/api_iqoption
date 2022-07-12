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

code = [1, 3, 6, 99, 4, 5, 101]
code_otc = [76, 77, 79]

if date.weekday() == 5 or date.weekday() == 6:
    dif_percent = 70
    dif_osc = 0.07
    actives_code = choices(code_otc)[0]
    print(f'iniciando a busca no ativo {actives[actives_code]}')
elif date.weekday() != 5 and date.weekday() != 6 and date.hour < 17:
    dif_percent = 60
    dif_osc = 0.06
    actives_code = choices(code)[0]
    print(f'iniciando a busca no ativo {actives[actives_code]}')
elif date.weekday() != 5 and date.weekday() != 6 and date.hour >= 17:
    dif_percent = 70
    dif_osc = 0.07
    actives_code = choices(code_otc)[0]
    print(f'iniciando a busca no ativo {actives[actives_code]}')

profit = API.get_profit(actives[actives_code], 'turbo')
balance = API.balance()

pot = 1000
value = pot

expect_value = value + (profit * value)

wins = []
loss = []

win_value = []
loss_value = []

red_analitics = []
green_analitics = []

osc_green = []
osc_red = []

one_minute_candle = [12, 17, 15, 7]
five_minutes_candles = [62]

one_minute = True
five_minutes = False


while True:

    try:
        
        if len(loss) >= 2:
            print('excedeu o limite de perdas')
            exit()
        
            
        if date.weekday() == 5 or date.weekday() == 6:
            
            dif_percent = 70
            dif_osc = 0.07
            actives_code = choices(code_otc)[0]
            print(f'buscando em {actives[actives_code]}')
            
            if len(green_analitics) > 0 and len(red_analitics) > 0:
                print(f'green: {sum(green_analitics)}%')
                print(f'red: {sum(red_analitics)}%')
                print(f'oscillation_red: {round(sum(osc_red), 3)}')
                print(f'oscillation_green: {round(sum(osc_green), 3)}')
            
        elif date.weekday() != 5 and date.weekday() != 6 and date.hour < 17:
            
            dif_percent = 60
            dif_osc = 0.06
            actives_code = choices(code)[0]
            print(f'buscando em {actives[actives_code]}')
            
            if len(green_analitics) > 0 and len(red_analitics) > 0:
                print(f'green: {sum(green_analitics)}%')
                print(f'red: {sum(red_analitics)}%')
                print(f'oscillation_red: {round(sum(osc_red), 3)}')
                print(f'oscillation_green: {round(sum(osc_green), 3)}')
            
        elif date.weekday() != 5 and date.weekday() != 6 and date.hour >= 17:
            
            dif_percent = 70
            dif_osc = 0.07
            actives_code = choices(code_otc)[0]
            print(f'buscando em {actives[actives_code]}')
            
            if len(green_analitics) > 0 and len(red_analitics) > 0:
                print(f'green: {sum(green_analitics)}%')
                print(f'red: {sum(red_analitics)}%')
                print(f'oscillation_red: {round(sum(osc_red), 3)}')
                print(f'oscillation_green: {round(sum(osc_green), 3)}')
            
        if one_minute:
            candles = API.get_all_candles(actives[actives_code], 60, choices(one_minute_candle)[0]) # 62 velas para decisões de 5 minutos e (12, 17) velas para 1 minuto
        elif five_minutes:
            candles = API.get_all_candles(actives[actives_code], 60, choices(five_minutes_candles)[0]) # 62 velas para decisões de 5 minutos e (12, 17) velas para 1 minuto

        candles = [{'close': i['close'], 'open': i['open'],
        'candle_color': 'red_candle' if i['open'] > i['close']
        else 'green_candle' if i['open'] < i['close'] else 'dogi'} for i in candles]
        
        media_candles = [{'osc_green':i['close'] - i['open'], 'osc_red': i['open'] - i['close']} for i in candles]

        red_candles = [x['candle_color']
            for x in candles if x['candle_color'] == 'red_candle']
        green_candles = [x['candle_color']
            for x in candles if x['candle_color'] == 'green_candle']
        
        total_candles = len(green_candles) + len(red_candles)
        percent_green = round(len(green_candles) / total_candles * 100)
        percent_red = round(len(red_candles) / total_candles * 100)
        
        if len(red_analitics) <= 4 and len(green_analitics) <= 4:
            
            for med_c in media_candles:
                
                if len(osc_green) <= 4 and len(osc_red) <= 4:
                    osc_green.append(med_c['osc_green'])
                    osc_red.append(med_c['osc_red'])
                else:
                    osc_green = []
                    osc_red = []
            
            red_analitics.append(percent_red)
            green_analitics.append(percent_green)
            
            if sum(green_analitics) > sum(red_analitics):
                critical_percent = sum(green_analitics) - sum(red_analitics)
            elif sum(green_analitics) < sum(red_analitics):
                critical_percent = sum(red_analitics) - sum(green_analitics)
        else:
            red_analitics = []
            green_analitics = []
                
        
        if sum(green_analitics) > sum(red_analitics) and critical_percent > dif_percent and round(sum(osc_green), 4) >= dif_osc:
            
            if one_minute:
                if balance > value:
                    status, id = API.call_or_put(value, actives[actives_code], 'put', 1)
                else:
                    print('saldo insuficiente')
                    exit()
            
            if five_minutes:
                if balance > value:
                    status, id = API.call_or_put(value, actives[actives_code], 'put', 5)
                else:
                    print('saldo insuficiente')
                    exit()
            
            print(f'venda: {sum(green_analitics)}%')
            print(f'compra: {sum(red_analitics)}%')
            
            print(f'oscillation: {round(sum(osc_green), 3)}')
                
            print(f'venda realizada de: R$ {round(value, 2)}')
            
            if status:
                status, check_value = API.check_win_or_loss(id, 'v4')
                
                if status == 'win':
                    wins.append(status)
                    win_value.append(check_value)
                    value = pot
                    
                    print(f'total wins: {len(wins)}, R$ {round(sum(win_value), 2)}')
                else:
                    loss.append(status)
                    loss_value.append(check_value)
                    new_pot = expect_value / profit
                    value = round(new_pot, 2)
                    
                    print(f'total loss: {len(loss)}, - R$ {round(sum(loss_value), 2) * - 1}')
        
        if sum(red_analitics) > sum(green_analitics) and critical_percent > dif_percent and round(sum(osc_red), 4) >= dif_osc:
            
            if one_minute:
                if balance > value:
                    status, id = API.call_or_put(value, actives[actives_code], 'call', 1)
                else:
                    print('saldo insuficiente')
                    exit()
            
            if five_minutes:
                if balance > value:
                    status, id = API.call_or_put(value, actives[actives_code], 'call', 5)
                else:
                    print('saldo insuficiente')
                    exit()
            
            print(f'venda: {sum(green_analitics)}%')
            print(f'compra: {sum(red_analitics)}%')
            
            print(f'oscillation: {round(sum(osc_red), 3)}')
                
            print(f'compra realizada de: R$ {round(value, 2)}')
            
            if status:
                status, check_value = API.check_win_or_loss(id, 'v4')
                
                if status == 'win':
                    wins.append(status)
                    win_value.append(check_value)
                    value = pot
                    
                    print(f'total wins: {len(wins)}, R$ {round(sum(win_value), 2)}')
                else:
                    loss.append(status)
                    loss_value.append(check_value)
                    new_pot = expect_value / profit
                    value = round(new_pot, 2)
                    
                    print(f'total loss: {len(loss)}, -R$ {round(sum(loss_value), 2) * - 1}')
            
                            
        API.set_time_sleep(.5)
    except Exception as error:
        print(f'something wrong: {error}')