# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option
import numpy as np

account_type = "REAL"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

balance = API.balance(account_type)
print(f'my account is {account_type}: R$ {balance}')
print('iniciando algoritimo')

wins = []
stop_loss = []

value = 6.35
active = 'EURUSD-OTC'


valid_red_candle = ['red', 'red', 'red', 'red']
valid_green_candle = ['green', 'green', 'green', 'green']

verify_candle = []
red = []
green = []
total_candles_tendence_line = 100
total_candles_in_array = 4

while True:
    
    try:
        
        five_minutes_candle = API.get_all_candles(active, 300, 1)
        fifteen_minutes_candle = API.get_all_candles(active, 900, 1)
        
        historic_five_minutes = API.get_all_candles(active, 300, 6)
    
        historic_five_m = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi'}
        for i in historic_five_minutes]
        
        for hist in historic_five_m:
            
            if hist['candle'] == 'red':
                if len(verify_candle) <= total_candles_in_array:
                    verify_candle.append(hist['candle'])
                else:
                    verify_candle = []
            
            if hist['candle'] == 'green':
                if len(verify_candle) <= total_candles_in_array:
                    verify_candle.append(hist['candle'])
                else:
                    verify_candle = []
            
            if len(verify_candle) > 0 and len(verify_candle) == total_candles_in_array:
                
                candle_fifteen_m = [{'candle': 'red' if i['open'] > i['close']
                else 'green' if i['open'] < i['close'] else 'dogi', 'open': i['open'], 'close': i['close'],
                'max': i['max'], 'min': i['min'], 'id': i['id']}
                for i in fifteen_minutes_candle]
                
                candle_five_m = [{'candle': 'red' if i['open'] > i['close']
                else 'green' if i['open'] < i['close'] else 'dogi', 'open': i['open'], 'close': i['close'],
                'max': i['max'], 'min': i['min'], 'id': i['id']}
                for i in five_minutes_candle]
                
                tl_fifteen_m = API.get_all_candles(active, 900, total_candles_tendence_line)
                
                scan_tl = [{'candle': 'red' if i['open'] > i['close']
                else 'green' if i['open'] < i['close'] else 'dogi'} for i in tl_fifteen_m]
                
                for scan in scan_tl:
                    
                    if len(red) <= total_candles_tendence_line:
                        if scan['candle'] == 'red':
                            red.append(scan['candle'])
                            
                    
                    if len(green) <= total_candles_tendence_line:
                        if scan['candle'] == 'green':
                            green.append(scan['candle'])
                            
                        
                    total_candles = len(green) + len(red)
                    
                    if total_candles == total_candles_tendence_line and len(red) > 0 and len(green) > 0:
                        
                        if len(red) > len(green):
                            print(f'green: {len(green)}')
                            print(f'red: {len(red)}')
                            print('tendencia de baixa')
                            
                        if len(red) < len(green):
                            print(f'green: {len(green)}')
                            print(f'red: {len(red)}')
                            print('tendencia de alta')
                        
                        if len(red) == len(green):
                            print(f'green: {len(green)}')
                            print(f'red: {len(red)}')
                            print('mercado consolidado, aguardando 20 minutos')
                            API.set_time_sleep(1200)

                        for candle_five in candle_five_m:
                            
                            for candle_fifteen in candle_fifteen_m:
                                
                                if len(red) > len(green) and np.array_equal(valid_red_candle, verify_candle) == True and candle_five['candle'] == 'red' and candle_fifteen['candle'] == 'red':
                                    
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
                                            
                                            if len(wins) == 2:
                                                print('meta batida')
                                                exit()
                                        else:
                                            stop_loss.append(status)
                                            print(f'total loss: {len(stop_loss)}')
                                            
                                            if len(stop_loss) == 1:
                                                print('stop loss acionado')
                                                exit()
                                                
                                if len(red) < len(green) and np.array_equal(valid_green_candle, verify_candle) == True and candle_five['candle'] == 'green' and candle_fifteen['candle'] == 'green':
                                    
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
                                            
                                            if len(wins) == 2:
                                                print('meta batida')
                                                exit()
                                        else:
                                            stop_loss.append(status)
                                            print(f'total loss: {len(stop_loss)}')
                                            
                                            if len(stop_loss) == 1:
                                                print('stop loss acionado')
                                                exit()
                            red = []
                            green = []
                        
                              
            
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')