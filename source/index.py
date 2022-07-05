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
        candles = [i['close'] for i in candles]
        
        ticks = API.get_ticks_real_time('EURUSD-OTC')
        
        for tick in ticks:
            
            pointer = round(ticks[tick]['close'], 4)
            max_pointer = round(max(candles), 4)
            min_pointer = round(min(candles), 4)
            print(pointer)
        
            if pointer == max_pointer:
                
                print(f'venda realizada de: R$ {value}')
                status, id = API.call_or_put(value, 'EURUSD-OTC', 'put', 1)
                
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
            
            if pointer == min_pointer:
                
                print(f'compra realizada de: R$ {value}')
                status, id = API.call_or_put(value, 'EURUSD-OTC', 'call', 1)
                
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