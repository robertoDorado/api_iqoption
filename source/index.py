#_*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option

API = BOT_IQ_Option()

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

value = 2.75

while True:
    try:
        
        ticks = API.get_ticks_real_time('EURUSD-OTC')
        
        for tick in ticks:
            
            pointer = round(ticks[tick]['close'], 4)
            print(pointer)
        
            if pointer == 0.8989:
                print(f'venda realizada de: {value}')
                status, id = API.call_or_put(value, 'EURUSD-OTC', 'put', 1)
                
                if status:
                    print(API.check_win_or_loss(id, 'v4'))
            
            if pointer == 0.8982:
                print(f'compra realizada de: {value}')         
                status, id = API.call_or_put(value, 'EURUSD-OTC', 'call', 1)
                
                if status:
                    print(API.check_win_or_loss(id, 'v4'))
              
        API.set_time_sleep(1)
    except Exception as error:
        print(f'something wrong: {error}')