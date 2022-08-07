# _*_ coding: utf-8 _*_
from asyncio.windows_events import NULL
from iqoption.connection import BOT_IQ_Option
from candlestick import candlestick
import pandas as pd

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

instance = API.get_instance()
balance = API.balance(account_type)

wins = []
stop_loss = []

value = balance * 0.1
total_candles = 30

high_tendencie = False
low_tendencie = False
consolidated_market = False

otc = True
mkt = False

if otc:
    active_index = 76
elif mkt:
    active_index = 1

active = API.get_all_actives()[active_index]

seconds = 0
decimal = 5

total_candles_df = total_candles
start = False

print(f'my account is {account_type}: R$ {balance}, no ativo {active}')
print('iniciando algoritimo')

while True:
    
    try:

        seconds += 1
        
        if mkt:
        
            indicators = instance.get_technical_indicators(active)
            
            if 'code' in indicators:
            
                if indicators['code'] == 'no_technical_indicator_available':
                    
                    seconds = 0
                    active_index += 1
                    
                    if otc and active_index > 80:
                        active_index = 76
                        
                    if mkt and active_index > 4:
                        active_index = 1
                        
                    active = API.get_all_actives()[active_index]
                    indicators = instance.get_technical_indicators(active)
                    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                    print(f'mudando para o ativo {active}')
        
        if seconds == 300:
            
            seconds = 0
            active_index += 1
            
            if otc and active_index > 80:
                active_index = 76
                
            if mkt and active_index > 4:
                active_index = 1
                
            active = API.get_all_actives()[active_index]
            if mkt:
                indicators = instance.get_technical_indicators(active)
            historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
            print(f'mudando para o ativo {active}')
        
        if mkt:
            indicators = [i for i in indicators if i['group'] == 'PIVOTS']
            indicators = [i for i in indicators if i['candle_size'] == 300]
            
            s3 = [i['value'] for i in indicators if i['name'] == 'Classic s3']
            s2 = [i['value'] for i in indicators if i['name'] == 'Classic s2']
            s1 = [i['value'] for i in indicators if i['name'] == 'Classic s1']
            
            p = [i['value'] for i in indicators if i['name'] == 'Classic p']
            
            r1 = [i['value'] for i in indicators if i['name'] == 'Classic r1']
            r2 = [i['value'] for i in indicators if i['name'] == 'Classic r2']
            r3 = [i['value'] for i in indicators if i['name'] == 'Classic r3']
        
        historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
        
        historic_five_minutes = [{'candle': 'red' if historic_five_minutes[i]['open'] > historic_five_minutes[i]['close']
        else 'green' if historic_five_minutes[i]['close'] > historic_five_minutes[i]['open'] else 'dogi',
        'close': historic_five_minutes[i]['close'], 'open': historic_five_minutes[i]['open'],
        'max': historic_five_minutes[i]['max'], 'min': historic_five_minutes[i]['min']}
        for i in historic_five_minutes]
        
        candles = API.get_all_candles(active, 300, total_candles_df)
        
        candles_df = pd.DataFrame.from_dict(candles)
        candles_df.rename(columns={'max':'high', 'min':'low'}, inplace=True)
        
        hammer = candlestick.hammer(candles_df, target='result')
        hammer = hammer.to_dict()
        
        inverted_hammer = candlestick.inverted_hammer(candles_df, target='result')
        inverted_hammer = inverted_hammer.to_dict()
        
        shooting_star = candlestick.shooting_star(candles_df, target='result')
        shooting_star = shooting_star.to_dict()
        
        hanging_man = candlestick.hanging_man(candles_df, target='result')
        hanging_man = hanging_man.to_dict()
        
        bearish_harami = candlestick.bearish_harami(candles_df, target='result')
        bearish_harami = bearish_harami.to_dict()
        
        bullish_harami = candlestick.bullish_harami(candles_df, target='result')
        bullish_harami = bullish_harami.to_dict()
        
        bearish_engulfing = candlestick.bearish_engulfing(candles_df, target='result')
        bearish_engulfing = bearish_engulfing.to_dict()
        
        bullish_engulfing = candlestick.bullish_engulfing(candles_df, target='result')
        bullish_engulfing = bullish_engulfing.to_dict()
        
        piercing_pattern = candlestick.piercing_pattern(candles_df, target='result')
        piercing_pattern = piercing_pattern.to_dict()
        
        dark_cloud_cover = candlestick.dark_cloud_cover(candles_df, target='result')
        dark_cloud_cover = dark_cloud_cover.to_dict()
        
        all_candle_max_five_m = [i['max'] for i in historic_five_minutes]
        all_candle_min_five_m = [i['min'] for i in historic_five_minutes]
        all_candle_open_five_m = [i['open'] for i in historic_five_minutes]
        all_candle_close_five_m = [i['close'] for i in historic_five_minutes]
        all_candle_color_five_m = [i['candle'] for i in historic_five_minutes]
        
        first_candle_index = len(all_candle_close_five_m) - 1
        second_candle_index = len(all_candle_close_five_m) - 2
        third_candle_index = len(all_candle_close_five_m) - 3
        
        red = [i['candle'] for i in historic_five_minutes if i['candle'] == 'red']
        green = [i['candle'] for i in historic_five_minutes if i['candle'] == 'green']
        
        max_df = round(all_candle_max_five_m[first_candle_index], 3)
        min_df = round(all_candle_min_five_m[first_candle_index], 3)
        
        if max_df == min_df:
            start = True
        
        if len(red) > len(green):
            high_tendencie = False
            low_tendencie = True
            consolidated_market = False
            print(f'red: {len(red)}')
            print(f'green: {len(green)}')
            
        if len(red) < len(green):
            high_tendencie = True
            low_tendencie = False
            consolidated_market = False
            print(f'red: {len(red)}')
            print(f'green: {len(green)}')

        if len(red) == len(green):
            high_tendencie = False
            low_tendencie = False
            consolidated_market = True
            print(f'red: {len(red)}')
            print(f'green: {len(green)}')
            
            
        if high_tendencie:
            print('tendencia de alta')
        
        if low_tendencie:
            print('tendencia de baixa')
        
        if consolidated_market:
            print('tendencia consolidada')
        
        
        # tomada de decisão em padrões de velas
        if low_tendencie and start and bullish_engulfing['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('engolfo de alta')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if low_tendencie and start and bullish_engulfing['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('engolfo de alta')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if low_tendencie and start and bullish_harami['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('harami de alta')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if low_tendencie and start and bullish_harami['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
                print('harami de alta')
                win = API.call_decision(balance, value, active, wins, stop_loss)
                
                if win == True:
                    active_index += 1
                        
                    if otc and active_index > 80:
                        active_index = 76
                        
                    if mkt and active_index > 4:
                        active_index = 1
                        
                    active = API.get_all_actives()[active_index]
                    if mkt:
                        indicators = instance.get_technical_indicators(active)
                    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                    print(f'mudando para o ativo {active}')
                
        if low_tendencie and start and hammer['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('martelo')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
        
                
        if low_tendencie and start and hammer['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('martelo')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if low_tendencie and start and inverted_hammer['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('martelo invertido')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if low_tendencie and start and inverted_hammer['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('martelo invertido')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
        
        if low_tendencie and start and piercing_pattern['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('piercing')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if low_tendencie and start and piercing_pattern['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] > all_candle_open_five_m[first_candle_index]:
            print('piercing')
            win = API.call_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if high_tendencie and start and bearish_engulfing['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('engolfo de baixa')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if high_tendencie and start and bearish_engulfing['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('engolfo de baixa')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if high_tendencie and start and bearish_harami['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('harami de baixa')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if high_tendencie and start and bearish_harami['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('harami de baixa')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
        
        if high_tendencie and start and shooting_star['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('estrela cadente')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if high_tendencie and start and shooting_star['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('estrela cadente')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if high_tendencie and start and hanging_man['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('enforcado')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
        
        if high_tendencie and start and hanging_man['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('enforcado')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
        if high_tendencie and start and dark_cloud_cover['result'][third_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('nuvem negra')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
        
        if high_tendencie and start and dark_cloud_cover['result'][second_candle_index] == True and all_candle_close_five_m[first_candle_index] < all_candle_open_five_m[first_candle_index]:
            print('nuvem negra')
            win = API.put_decision(balance, value, active, wins, stop_loss)
            
            if win == True:
                active_index += 1
                    
                if otc and active_index > 80:
                    active_index = 76
                    
                if mkt and active_index > 4:
                    active_index = 1
                    
                active = API.get_all_actives()[active_index]
                if mkt:
                    indicators = instance.get_technical_indicators(active)
                historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                print(f'mudando para o ativo {active}')
                
                
                
                
                
                
                
        
        # Tomada de decisão em suporte e resistencia
        if mkt == True and otc == False:
            if round(all_candle_close_five_m[first_candle_index], decimal) == round(s1[0], decimal) or round(all_candle_close_five_m[first_candle_index], decimal) == round(s2[0], decimal) or round(all_candle_close_five_m[first_candle_index], decimal) == round(s3[0], decimal):
                print('igualou ao suporte')
                win = API.call_decision(balance, value, active, wins, total_candles, stop_loss, otc, mkt, active_index)
                
                if win == True:
                    active_index += 1
                        
                    if otc and active_index > 80:
                        active_index = 76
                        
                    if mkt and active_index > 4:
                        active_index = 1
                        
                    active = API.get_all_actives()[active_index]
                    if mkt:
                        indicators = instance.get_technical_indicators(active)
                    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                    print(f'mudando para o ativo {active}')
        
                    
                            
            if round(all_candle_close_five_m[first_candle_index], decimal) == round(r1[0], decimal) or round(all_candle_close_five_m[first_candle_index], decimal) == round(r2[0], decimal) or round(all_candle_close_five_m[first_candle_index], decimal) == round(r3[0], decimal):
                print('igualou a resistencia')
                win = API.put_decision(balance, value, active, wins, total_candles, stop_loss, otc, mkt, active_index)
                
                if win == True:
                    active_index += 1
                        
                    if otc and active_index > 80:
                        active_index = 76
                        
                    if mkt and active_index > 4:
                        active_index = 1
                        
                    active = API.get_all_actives()[active_index]
                    if mkt:
                        indicators = instance.get_technical_indicators(active)
                    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                    print(f'mudando para o ativo {active}')    
                

            # Tomada de decisão referente aos rompimentos
            if start and all_candle_close_five_m[second_candle_index] < s1[0] or all_candle_close_five_m[second_candle_index] < s2[0] or all_candle_close_five_m[second_candle_index] < s3[0] and start:
                print('rompeu em baixa')
                win = API.put_decision(balance, value, active, wins, total_candles, stop_loss, otc, mkt, active_index)
                
                if win == True:
                    active_index += 1
                        
                    if otc and active_index > 80:
                        active_index = 76
                        
                    if mkt and active_index > 4:
                        active_index = 1
                        
                    active = API.get_all_actives()[active_index]
                    if mkt:
                        indicators = instance.get_technical_indicators(active)
                    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                    print(f'mudando para o ativo {active}')
            
            if high_tendencie == True and start and all_candle_close_five_m[second_candle_index] > r1[0] or all_candle_close_five_m[second_candle_index] > r2[0] or all_candle_close_five_m[second_candle_index] > r3[0]:
                print('rompeu em alta')
                win = API.call_decision(balance, value, active, wins, total_candles, stop_loss, otc, mkt, active_index)
                
                if win == True:
                    active_index += 1
                        
                    if otc and active_index > 80:
                        active_index = 76
                        
                    if mkt and active_index > 4:
                        active_index = 1
                        
                    active = API.get_all_actives()[active_index]
                    if mkt:
                        indicators = instance.get_technical_indicators(active)
                    historic_five_minutes = API.get_realtime_candles(active, 300, total_candles)
                    print(f'mudando para o ativo {active}')
                            
        API.set_time_sleep(.5)
    except Exception as error:
        print(f'exception: {error}')