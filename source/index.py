#_*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option

API = BOT_IQ_Option()

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

value = 2.75

wins = []
loss = []

win_value = []
loss_value = []

while True:
    
    try:
        
        candles = API.get_all_candles('EURUSD-OTC', 60, 100)
        
        ticks = API.get_ticks_real_time('EURUSD-OTC')
        
        candles = [{'close': i['close'], 'open': i['open'], 
        'candle_color': 'red_candle' if i['open'] > i['close'] 
        else 'green_candle' if i['open'] < i['close'] else 'dogi'} for i in candles]
        
        red_candles = [x['candle_color'] for x in candles if x['candle_color'] == 'red_candle']
        green_candles = [x['candle_color'] for x in candles if x['candle_color'] == 'green_candle']
        
        for tick in ticks:
            
            pointer = round(ticks[tick]['close'], 4)
            print(pointer)
        
            if len(green_candles) > len(red_candles):
                
                print(f'venda realizada de: R$ {value}')
                status, id = API.call_or_put(value, 'EURUSD-OTC', 'put', 1)
                
                if status:
                    status, check_value = API.check_win_or_loss(id, 'v4')
                    
                    if status == 'win':
                        wins.append(status)
                        win_value.append(check_value)
                        
                        print(f'total wins: {len(wins)}, R$ {round(sum(win_value), 2)}')
                        API.set_time_sleep(60)
                    else:
                        loss.append(status)
                        loss_value.append(check_value)
                        
                        print(f'total loss: {len(loss)}, - R$ {round(sum(loss_value), 2) * - 1}')
                        API.set_time_sleep(60)
            
            if len(green_candles) < len(red_candles):
                
                print(f'compra realizada de: R$ {value}')
                status, id = API.call_or_put(value, 'EURUSD-OTC', 'call', 1)
                
                if status:
                    status, check_value = API.check_win_or_loss(id, 'v4')
                    
                    if status == 'win':
                        wins.append(status)
                        win_value.append(check_value)
                        
                        print(f'total wins: {len(wins)}, R$ {round(sum(win_value), 2)}')
                        API.set_time_sleep(60)
                    else:
                        loss.append(status)
                        loss_value.append(check_value)
                        
                        print(f'total loss: {len(loss)}, -R$ {round(sum(loss_value), 2) * - 1}')
                        API.set_time_sleep(60)
                            
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')