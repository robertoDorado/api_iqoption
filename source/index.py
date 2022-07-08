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

if date.hour > 14:
    actives_code = choices(actives_code_otc)[0]
else:
    actives_code = choices(actives_code)[0]

profit = API.get_profit(actives[actives_code], 'turbo') * 100
    
value = 1000

wins = []
loss = []

win_value = []
loss_value = []
i = 0

while True:

    try:
        
        i = i + 1
        
        if i == 10:
            if date.hour > 14:
                actives_code = choices(actives_code_otc)[0]
                print(f'buscando em {actives[actives_code]}')
            else:
                actives_code = choices(actives_code)[0]
                print(f'buscando em {actives[actives_code]}')
            i = 0
        
        candles = API.get_all_candles(actives[actives_code], 60, 11)

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

        if percent_green >= 75 and percent_green > percent_red:
            
            if value > 0:
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
                    
                    if len(wins) > 0 or len(loss) > 0:
                        
                        total_universe = len(wins) + len(loss)
                    
                        prob_wins = len(wins) / total_universe
                        prob_loss = 1 - prob_wins
                    
                        k = API.kelly_discretion(prob_wins, prob_loss, profit)
                        value = value + (value * (round(k, 2) / 100))
                    
                    print(f'total wins: {len(wins)}, R$ {round(sum(win_value), 2)}')
                else:
                    loss.append(status)
                    loss_value.append(check_value)
                    
                    if len(wins) > 0 or len(loss) > 0:
                        
                        total_universe = len(wins) + len(loss)
                
                        prob_wins = len(wins) / total_universe
                        prob_loss = 1 - prob_wins
                    
                        k = API.kelly_discretion(prob_wins, prob_loss, profit)
                        value = value - (value * (round(k, 2) / 100))
                    
                    print(f'total loss: {len(loss)}, - R$ {round(sum(loss_value), 2) * - 1}')
        
        if percent_red >= 75 and percent_red > percent_green:
            
            if value > 0:
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
                    
                    if len(wins) > 0 or len(loss) > 0:
                        
                        total_universe = len(wins) + len(loss)
                
                        prob_wins = len(wins) / total_universe
                        prob_loss = 1 - prob_wins
                        
                        k = API.kelly_discretion(prob_wins, prob_loss, profit)
                        value = value + (value * (round(k, 2) / 100))
                    
                    print(f'total wins: {len(wins)}, R$ {round(sum(win_value), 2)}')
                else:
                    loss.append(status)
                    loss_value.append(check_value)
                    
                    if len(wins) > 0 or len(loss) > 0:
                        
                        total_universe = len(wins) + len(loss)
                
                        prob_wins = len(wins) / total_universe
                        prob_loss = 1 - prob_wins
                        
                        k = API.kelly_discretion(prob_wins, prob_loss, profit)
                        value = value - (value * (round(k, 2) / 100))
                        
                    
                    print(f'total loss: {len(loss)}, -R$ {round(sum(loss_value), 2) * - 1}')
                            
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')