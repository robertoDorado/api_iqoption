# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option

account_type = "REAL"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)

wins = []
stop_loss = []

value = 7.25
active_index = 76
active = API.get_all_actives()[active_index]

total_candles = 50

height_tendencie = False
low_tendencie = False
consolidated_market = False

otc = True
mkt = False

seconds = 0

print(f'my account is {account_type}: R$ {balance}, no ativo {active}')
print('iniciando algoritimo')

while True:
    
    try:
        
        seconds += 1 
        
        if seconds == 3600:
            seconds = 0
            active_index += 1
            
            if otc and active_index > 80:
                active_index = 76
                
            if mkt and active_index > 4:
                active_index = 1
                
            active = API.get_all_actives()[active_index]
            print(f'mudando para o ativo {active}')
        
        historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
        historic_fifteen_minutes = API.get_all_candles(active, 900, 1)
        
        historic_five_minutes = [{'candle': 'red' if historic_five_minutes[i]['open'] > historic_five_minutes[i]['close']
        else 'green' if historic_five_minutes[i]['close'] > historic_five_minutes[i]['open'] else 'dogi',
        'max': historic_five_minutes[i]['max'] if 'max' in historic_five_minutes[i] else NULL,
        'min': historic_five_minutes[i]['min'] if 'min' in historic_five_minutes[i] else NULL,
        'close': historic_five_minutes[i]['close']}
        for i in historic_five_minutes]
        
        # current_reference_index = len(historic_five_minutes) - 1
        # current_reference = historic_five_minutes[current_reference_index]
        
        all_candles_five_m = [i['candle'] for i in historic_five_minutes]
        all_candle_max_five_m = [i['max'] for i in historic_five_minutes]
        all_candle_min_five_m = [i['min'] for i in historic_five_minutes]
        all_candle_close_five_m = [i['close'] for i in historic_five_minutes]
        
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
            
        first_candle_index_five_m = len(all_candles_five_m) - 1
        
        second_candle_index_five_m = len(all_candles_five_m) - 2
        second_max_candle_index = len(all_candle_max_five_m) - 2
        second_min_candle_index = len(all_candle_min_five_m) - 2
        second_close_candle_index = len(all_candle_close_five_m) - 2
        
        # print(f'first candle color: {all_candles_five_m[first_candle_index_five_m]}')
        # print(f'second candle color: {all_candles_five_m[second_candle_index_five_m]}')
        # print('\n')
        # print(f'second max candle: {all_candle_max_five_m[second_max_candle_index]}')
        # print(f'second min candle: {all_candle_min_five_m[second_min_candle_index]}')
        # print('\n')
        # print(f'second close five minutes: {all_candle_close_five_m[second_close_candle_index]}')
        
        
        candle_fifteen_m = [{'candle': 'red' if i['open'] > i['close'] else 'green' if i['close'] > i['open'] else 'dogi',
        'max': i['max'], 'min':i['min'], 'close': i['close']} for i in historic_fifteen_minutes]
        
        candle_color_fifteen_m = [i['candle'] for i in candle_fifteen_m]
        
        if low_tendencie and all_candles_five_m[first_candle_index_five_m] == 'red' and all_candles_five_m[second_candle_index_five_m] == 'red' and candle_color_fifteen_m[0] == 'red' and all_candle_close_five_m[second_close_candle_index] < all_candle_min_five_m[second_min_candle_index]:
                
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
        
        
        if height_tendencie and all_candles_five_m[first_candle_index_five_m] == 'green' and all_candles_five_m[second_candle_index_five_m] == 'green' and candle_color_fifteen_m[0] == 'green' and all_candle_close_five_m[second_close_candle_index] > all_candle_max_five_m[second_max_candle_index]:
                
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