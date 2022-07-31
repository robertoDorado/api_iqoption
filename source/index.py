# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option
import numpy as np

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)
print(f'my account is {account_type}: R$ {balance}')
print('iniciando algoritimo')

wins = []
stop_loss = []

value = 10000
active = 'EURUSD-OTC'

total_candles = 50

height_tendencie = False
low_tendencie = False
consolidated_market = False

while True:
    
    try:
        
        historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
        historic_fifteen_minutes = API.get_all_candles(active, 900, 1)
        
        historic_five_minutes = [{'candle': 'red' if historic_five_minutes[i]['open'] > historic_five_minutes[i]['close']
        else 'green' if historic_five_minutes[i]['close'] > historic_five_minutes[i]['open'] else 'dogi',
        'ask': historic_five_minutes[i]['ask'] if 'ask' in historic_five_minutes[i] else NULL,
        'bid': historic_five_minutes[i]['bid'] if 'bid' in historic_five_minutes[i] else NULL,
        'close': historic_five_minutes[i]['close']}
        for i in historic_five_minutes]
        
        current_reference_index = len(historic_five_minutes) - 1
        current_reference = historic_five_minutes[current_reference_index]
        
        all_candles_five_m = [i['candle'] for i in historic_five_minutes]
        
        red = [i['candle'] for i in historic_five_minutes if i['candle'] == 'red']
        green = [i['candle'] for i in historic_five_minutes if i['candle'] == 'green']
        
        if len(red) > len(green):
            height_tendencie = False
            low_tendencie = True
            consolidated_market = False
            print(f'red: {len(red)}')
            print(f'green: {len(green)}')
            
        if len(red) < len(green):
            height_tendencie = True
            low_tendencie = False
            consolidated_market = False
            print(f'red: {len(red)}')
            print(f'green: {len(green)}')

        if len(red) == len(green):
            height_tendencie = False
            low_tendencie = False
            consolidated_market = True
            print(f'red: {len(red)}')
            print(f'green: {len(green)}')
            
            
        if height_tendencie:
            print('tendencia de alta')
        
        if low_tendencie:
            print('tendencia de baixa')
        
        if consolidated_market:
            print('tendencia consolidada')
            
        first_index = len(all_candles_five_m) - 1
        second_index = len(all_candles_five_m) - 2
        third_index = len(all_candles_five_m) - 3
        fourth_index = len(all_candles_five_m) - 4
        
        candle_fifteen_m = [{'candle': 'red' if i['open'] > i['close'] else 'green' if i['close'] > i['open'] else 'dogi'
        for i in historic_fifteen_minutes}]
        
        candle_fifteen_m = [i['candle'] for i in candle_fifteen_m]
        
        if low_tendencie and all_candles_five_m[first_index] == 'red' and all_candles_five_m[second_index] == 'red' and all_candles_five_m[third_index] == 'red' and all_candles_five_m[fourth_index] == 'red' and candle_fifteen_m[0] == 'red' and current_reference['close'] < current_reference['bid']:
                
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
        
        
        if height_tendencie and all_candles_five_m[first_index] == 'green' and all_candles_five_m[second_index] == 'green' and all_candles_five_m[third_index] == 'green' and all_candles_five_m[fourth_index] == 'green' and candle_fifteen_m[0] == 'green' and current_reference['close'] > current_reference['ask']:
                
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
                            
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')