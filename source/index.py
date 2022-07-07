#_*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option

API = BOT_IQ_Option()

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()
    
balance = API.balance() * 0.1
active = API.get_all_actives()[76] #EURUSD-OTC
profit = API.get_profit(active, 'turbo') * 100

value = 100

wins = []
loss = []

win_value = []
loss_value = []

while True:
    
    try:
        
        candles = API.get_all_candles('EURUSD-OTC', 60, 100)
        
        candles = [{'close': i['close'], 'open': i['open'], 
        'candle_color': 'red_candle' if i['open'] > i['close'] 
        else 'green_candle' if i['open'] < i['close'] else 'dogi'} for i in candles]
        
        red_candles = [x['candle_color'] for x in candles if x['candle_color'] == 'red_candle']
        green_candles = [x['candle_color'] for x in candles if x['candle_color'] == 'green_candle']
        
        
        if len(green_candles) > len(red_candles):
            
            print(f'venda realizada de: R$ {round(value, 2)}')
            
            if value > 0:
                status, id = API.call_or_put(value, 'EURUSD-OTC', 'put', 1)
            else:
                print('saldo insuficiente')
                exit()
            
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
        
        if len(green_candles) < len(red_candles):
            
            print(f'compra realizada de: R$ {round(value, 2)}')
            
            if value > 0:
                status, id = API.call_or_put(value, 'EURUSD-OTC', 'call', 1)
            else:
                print('saldo insuficiente')
                exit()
            
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
                
                        prob_wins = len(wins) / total_universe
                        prob_loss = 1 - prob_wins
                        
                        k = API.kelly_discretion(prob_wins, prob_loss, profit)
                        value = value - (value * (round(k, 2) / 100))
                        
                    
                    print(f'total loss: {len(loss)}, -R$ {round(sum(loss_value), 2) * - 1}')
                            
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')