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

valid_four_red_candle = ['red', 'red', 'red', 'red']
valid_four_green_candle = ['green', 'green', 'green', 'green']

valid_five_red_candle = ['red', 'red', 'red', 'red', 'red']
valid_five_green_candle = ['green', 'green', 'green', 'green', 'green']

total_candles_tendence_line = 50
total_candles_in_array = 4

height_tendencie = False
low_tendencie = False
consolidated_market = False

while True:
    
    try:
        
        market_tendencie = API.get_all_candles(active, 300, total_candles_tendence_line)
        historic_five_minutes = API.get_realtime_candles(active, 300, total_candles_in_array)
        historic_fifteen_minutes = API.get_all_candles(active, 900, 1)
        
        market_tendencie = ['red' if i['open'] > i['close']
        else 'green' if i['close'] > i['open'] else 'dogi'
        for i in market_tendencie]
        
        historic_fifteen_minutes = ['red' if i['open'] > i['close']
        else 'green' if i['close'] > i['open'] else 'dogi'
        for i in historic_fifteen_minutes]
        
        red = [i for i in market_tendencie if 'red' in i]
        green = [i for i in market_tendencie if 'green' in i]
        
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
        
        
        verify_candles = ['red' if historic_five_minutes[i]['open'] > historic_five_minutes[i]['close']
        else 'green' if historic_five_minutes[i]['close'] > historic_five_minutes[i]['open'] else 'dogi'
        for i in historic_five_minutes]
        
        
        if height_tendencie:
            print('tendencia de alta')
        
        if low_tendencie:
            print('tendencia de baixa')
        
        if consolidated_market:
            print('tendencia consolidada')
        
        
        for candle_fifteen in historic_fifteen_minutes:
            
            index_current_element = len(verify_candles) - 1
            current_five_m_candle = verify_candles[index_current_element]
            
            if low_tendencie == True and np.array_equal(valid_four_red_candle, verify_candles) == True or np.array_equal(valid_five_red_candle, verify_candles) == True and current_five_m_candle == 'red' and candle_fifteen == 'red':
                
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
                            
            if height_tendencie == True and np.array_equal(valid_four_green_candle, verify_candles) == True or np.array_equal(valid_five_green_candle, verify_candles) == True and current_five_m_candle == 'green' and candle_fifteen == 'green':
                
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