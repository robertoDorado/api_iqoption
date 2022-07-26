# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from random import choices
from datetime import datetime

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

balance = API.balance(account_type)
print(f'my account is {account_type}: R$ {balance}')

red = []
green = []

wins = []
stop_loss = []

value = 10000
active = 'EURUSD-OTC'

while True:
    
    try:
        
        five_minutes_candle = API.get_all_candles(active, 300, 1)
        fifteen_minutes_candle = API.get_all_candles(active, 900, 1)
        
        candle_fifteen_m = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi', 'open': i['open'], 'close': i['close']}
        for i in fifteen_minutes_candle]
        
        candle_five_m = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi', 'open': i['open'], 'close': i['close'],
        'max': i['max'], 'min': i['min'], 'id': i['id']}
        for i in five_minutes_candle]
        
        tl_five = API.get_all_candles(active, 300, 50)
        scan_tl = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi'} for i in tl_five]
        
        ticks = API.get_ticks_real_time(active, 300, 1)
        
        for tick in ticks:
            
            pointer = ticks[tick]['close']
        
            for i in scan_tl:
                
                if i['candle'] == 'red':
                    red.append(i['candle'])
                    
                if i['candle'] == 'green':
                    green.append(i['candle'])
                    
                for candle_five in candle_five_m:
                    
                    for candle_fifteen in candle_fifteen_m:
                        
                        min_candle_five = candle_five['min']
                        max_candle_five = candle_five['max']
                        
                        if len(green) > len(red) and candle_five['candle'] == 'green' and candle_fifteen['candle'] == 'green' and pointer > max_candle_five:
                            
                            if balance >= value:
                                status, id = API.call_or_put(value, active, 'call', 1)
                            else:
                                print('saldo insuficiente')
                                exit()
                            
                            print(f'compra: {value}')
                                
                            if status:
                                status, check_value = API.check_win_or_loss(id, 'v4')
                                
                                if status == 'win':
                                    wins.append(status)
                                    
                                    print(f'total wins: {len(wins)}')
                                else:
                                    stop_loss.append(status)
                                    print(f'total loss: {len(stop_loss)}')
                                    
                                    if len(stop_loss) == 1:
                                        print('stop loss acionado')
                                        exit()
                                    
                                    
                        
                        if len(green) < len(red) and candle_five['candle'] == 'red' and candle_fifteen['candle'] == 'red' and pointer < min_candle_five:
                            
                            if balance >= value:
                                status, id = API.call_or_put(value, active, 'put', 1)
                            else:
                                print('saldo insuficiente')
                                exit()
                            
                            print(f'venda: {value}')
                            
                            if status:
                                status, check_value = API.check_win_or_loss(id, 'v4')
                                
                                if status == 'win':
                                    wins.append(status)
                                    print(f'total wins: {len(wins)}')
                                else:
                                    stop_loss.append(status)
                                    print(f'total loss: {len(stop_loss)}')
                                    
                                    if len(stop_loss) == 1:
                                        print('stop loss acionado')
                                        exit()
            
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')