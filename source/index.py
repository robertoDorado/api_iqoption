# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

balance = API.balance(account_type)
print(f'my account is {account_type}: R$ {balance}')
print('iniciando algoritimo')

red = []
green = []

wins = []
stop_loss = []

value = 10000
active = 'EURJPY'


pullback_up = False
pullback_down = False

verify_red_candle = []
verify_green_candle = []

while True:
    
    try:
        
        five_minutes_candle = API.get_all_candles(active, 300, 1)
        fifteen_minutes_candle = API.get_all_candles(active, 900, 1)
        
        historic_five_minutes = API.get_all_candles(active, 300, 5)
        
        historic_five_m = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi'}
        for i in historic_five_minutes]
        
        
        for hist in historic_five_m:
            
            if hist['candle'] == 'red':
                verify_red_candle.append(hist['candle'])
            
            if hist['candle'] == 'green':
                verify_green_candle.append(hist['candle'])
        
        
        candle_fifteen_m = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi', 'open': i['open'], 'close': i['close'],
        'max': i['max'], 'min': i['min'], 'id': i['id']}
        for i in fifteen_minutes_candle]
        
        candle_five_m = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi', 'open': i['open'], 'close': i['close'],
        'max': i['max'], 'min': i['min'], 'id': i['id']}
        for i in five_minutes_candle]
        
        tl_five_m = API.get_all_candles(active, 300, 50)
        scan_tl = [{'candle': 'red' if i['open'] > i['close']
        else 'green' if i['open'] < i['close'] else 'dogi'} for i in tl_five_m]
        
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
                    
                    half_candle_fifteen = candle_fifteen['max'] + candle_fifteen['min'] / 2
                    half_candle_five = candle_five['max'] + candle_five['min'] / 2
                    
                    candle_force_min = candle_five['min'] + half_candle_five
                    candle_force_max = candle_five['max'] + half_candle_five
                    
                    
                    # possibilidade de rompimento em baixa
                    if len(verify_green_candle) == 0 and candle_fifteen['candle'] == 'red' and len(green) < len(red):
                        
                        if balance >= value:
                            status, id = API.call_or_put(value, active, 'put', 1)
                        else:
                            print('saldo insuficiente')
                            exit()
                        
                        print(f'compra: {value}')
                        print('possivel rompimento em baixa')
                        
                        if status:
                            status, check_value = API.check_win_or_loss(id, 'v4')
                            
                            if status == 'win':
                                wins.append(status)
                                print(f'total wins: {len(wins)}')
                                
                                API.set_time_sleep(300)
                                
                                # Região do pullback em tendencia de baixa
                                if candle_five['candle'] == 'green' and len(wins) == 1:
                                    pullback_up = True
                                
                                if len(wins) == 2:
                                    print('meta batida')
                                    exit()
                            else:
                                stop_loss.append(status)
                                print(f'total loss: {len(stop_loss)}')
                                
                                if len(stop_loss) == 1:
                                    print('stop loss acionado')
                                    exit()
                        
                    
                    #possibilidade de rompimento em alta
                    if len(verify_red_candle) == 0 and candle_fifteen['candle'] == 'green' and len(green) > len(red):
                        
                        if balance >= value:
                            status, id = API.call_or_put(value, active, 'call', 1)
                        else:
                            print('saldo insuficiente')
                            exit()
                        
                        print(f'compra: {value}')
                        print('possivel rompimento em alta')
                        
                        if status:
                            status, check_value = API.check_win_or_loss(id, 'v4')
                            
                            if status == 'win':
                                wins.append(status)
                                print(f'total wins: {len(wins)}')
                                
                                API.set_time_sleep(300)
                                
                                # Região do pullback em tendencia de alta
                                if candle_five['candle'] == 'red' and len(wins) == 1:
                                    pullback_down = True
                                
                                if len(wins) == 2:
                                    print('meta batida')
                                    exit()
                            else:
                                stop_loss.append(status)
                                print(f'total loss: {len(stop_loss)}')
                                
                                if len(stop_loss) == 1:
                                    print('stop loss acionado')
                                    exit()
                        
                    
                    
                    if len(green) > len(red):
                        print('tendencia de alta')
                    
                    if len(green) < len(red):
                        print('tendencia de baixa')
                        
                    if len(green) == len(red):
                        print('tendencia consolidada, aguardando 4 horas')
                        print(f'green: {len(green)}')
                        print(f'red: {len(red)}')
                        API.set_time_sleep(15000)
                        
                        
                    
                    # pullback de alta
                    if pullback_up == True and candle_five['candle'] == 'green':
                        
                        if balance >= value:
                            status, id = API.call_or_put(value, active, 'call', 1)
                        else:
                            print('saldo insuficiente')
                            exit()
                        
                        print(f'compra: {value}')
                        print('pullback vela verde')
                        
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
                        
                    
                    
                    # pullback de baixa
                    if pullback_down == True and candle_five['candle'] == 'red':
                        
                        if balance >= value:
                            status, id = API.call_or_put(value, active, 'put', 1)
                        else:
                            print('saldo insuficiente')
                            exit()
                        
                        print(f'venda: {value}')
                        print('pullback vela vermelha')
                        
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
                        
                        
                        
                    # Tomada de decisão em rompimento de alta, compra
                    if len(green) > len(red) and candle_five['candle'] == 'green' and candle_fifteen['candle'] == 'green' and pointer > candle_force_max and pointer > half_candle_fifteen:
                        
                        if balance >= value:
                            status, id = API.call_or_put(value, active, 'call', 1)
                        else:
                            print('saldo insuficiente')
                            exit()
                        
                        print(f'compra: {value}')
                        print('rompimento em alta')
                            
                        if status:
                            status, check_value = API.check_win_or_loss(id, 'v4')
                            
                            if status == 'win':
                                wins.append(status)
                                print(f'total wins: {len(wins)}')
                                API.set_time_sleep(300)
                                
                                # Região do pullback em tendencia de alta
                                if candle_five['candle'] == 'red' and len(wins) == 1:
                                    pullback_down = True
                                
                                if len(wins) == 2:
                                    print('meta batida')
                                    exit()
                            else:
                                stop_loss.append(status)
                                print(f'total loss: {len(stop_loss)}')
                                
                                if len(stop_loss) == 1:
                                    print('stop loss acionado')
                                    exit()
                                
                    
                    
                    
                            
                    # Tomada de decisão em rompimento de baixa, venda
                    if len(green) < len(red) and candle_five['candle'] == 'red' and candle_fifteen['candle'] == 'red' and pointer < candle_force_min and pointer < half_candle_fifteen:
                        
                        if balance >= value:
                            status, id = API.call_or_put(value, active, 'put', 1)
                        else:
                            print('saldo insuficiente')
                            exit()
                        
                        print(f'venda: {value}')
                        print('rompimento em baixa')
                        
                        if status:
                            status, check_value = API.check_win_or_loss(id, 'v4')
                            
                            if status == 'win':
                                wins.append(status)
                                print(f'total wins: {len(wins)}')
                                API.set_time_sleep(300)
                                
                                # Região do pullback em tendencia de baixa
                                if candle_five['candle'] == 'green' and len(wins) == 1:
                                    pullback_up = True
                                    
                                    if balance >= value:
                                        status, id = API.call_or_put(value, active, 'call', 1)
                                    else:
                                        print('saldo insuficiente')
                                        exit()
                                
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