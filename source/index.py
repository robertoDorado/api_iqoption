# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)

wins = []
stop_loss = []

value = 10000
active_index = 1
active = API.get_all_actives()[active_index]

total_candles = 80

height_tendencie = False
low_tendencie = False
consolidated_market = False

otc = False
mkt = True

seconds = 0

print(f'my account is {account_type}: R$ {balance}, no ativo {active}')
print('iniciando algoritimo')

while True:
    
    try:
        
        seconds += 1 
        
        if seconds == 300:
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
        
        
        all_candles_five_m = [i['candle'] for i in historic_five_minutes]
        all_candle_max_five_m = [i['max'] for i in historic_five_minutes]
        all_candle_min_five_m = [i['min'] for i in historic_five_minutes]
        all_candle_close_five_m = [i['close'] for i in historic_five_minutes]
        
        max_value_reference = max(all_candle_max_five_m)
        min_value_reference = min(all_candle_min_five_m)
        
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
            
        
        first_max_candle_index = len(all_candle_max_five_m) - 1
        first_min_candle_index = len(all_candle_min_five_m) - 1
        first_close_candle_index = len(all_candle_close_five_m) - 1
        
        if low_tendencie == True and all_candle_close_five_m[first_close_candle_index] < min_value_reference:
                
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
                        
                        active_index += 1
                        
                        if otc and active_index > 80:
                            active_index = 76
                            
                        if mkt and active_index > 4:
                            active_index = 1
                            
                        print(f'mudando para o ativo {active}')
                        
                        # if len(wins) == 2:
                        #     print('meta batida')
                        #     exit()
                    else:
                        stop_loss.append(status)
                        print(f'total loss: {len(stop_loss)}')
                        
                        if len(stop_loss) == 1:
                            print('stop loss acionado')
                            exit()
        
        
        if height_tendencie == True and all_candle_close_five_m[first_close_candle_index] > max_value_reference:
                
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
                        
                        active_index += 1
                        
                        if otc and active_index > 80:
                            active_index = 76
                            
                        if mkt and active_index > 4:
                            active_index = 1
                            
                        print(f'mudando para o ativo {active}')
                        
                        # if len(wins) == 2:
                        #     print('meta batida')
                        #     exit()
                    else:
                        stop_loss.append(status)
                        print(f'total loss: {len(stop_loss)}')
                        
                        if len(stop_loss) == 1:
                            print('stop loss acionado')
                            exit()
                            
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')