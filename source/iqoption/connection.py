from asyncio.windows_events import NULL
from iqoptionapi.stable_api import IQ_Option
import time
from datetime import datetime
from pytz import timezone
from components.helpers import *

class BOT_IQ_Option:
    
    def __init__(self, account_type):
        self.email = 'robertodorado7@gmail.com'
        self.password = 'Rob@19101910'
        self.instance = IQ_Option(self.email, self.password, account_type)
        self.current_timestamp = time.time()
    
    def conn(self):
        self.instance.connect()
        return self.instance.check_connect()
    
    def check_my_connection(self):
        return self.conn()
    
    def account_type(self, type):
        return self.instance.change_balance(type)
    
    def get_instance(self):
        return self.instance
    
    def get_profile_data(self, key):
        profile = self.instance.get_profile_ansyc()
        return profile[key]
    
    def get_all_candles(self, active='EURUSD', seconds=60, quant=3):
        
        try:
            dictionary_actives = self.instance.get_all_ACTIVES_OPCODE()
            for actives in list(dictionary_actives.keys()):
                if actives == active:
                    return self.instance.get_candles(active, seconds, quant, self.current_timestamp)
        except Exception:
            print('is not a valid active')
        
            
    def get_current_timestamp(self):
        return self.current_timestamp
    
    def convert_timestamp(self, timestamp=time.time(), tz='America/Sao_Paulo'):
        return datetime.fromtimestamp(timestamp, timezone(tz))
    
    def merge_candles(self, candle_a, candle_b):
        return candle_a + candle_b
    
    def set_time_sleep(self, value):
        return time.sleep(value)
    
    def get_ticks_real_time(self, active='EURUSD', size=60, maxdict=1):
        
        self.instance.start_candles_stream(active, size, maxdict)
        ticks = self.instance.get_realtime_candles(active, size)
        
        self.instance.stop_candles_stream(active, size)
        return ticks
    
    def get_mood_traders(self, active='EURUSD'):
        
        self.instance.start_mood_stream(active)
        mood = self.instance.get_traders_mood(active)
        
        self.instance.stop_mood_stream(active)
        return mood
    
    def get_all_actives(self, act=True):
        
        if act:
            return {code:act for act,code in self.instance.get_all_ACTIVES_OPCODE().items()}
        else:
            return self.instance.get_all_ACTIVES_OPCODE()
    
    def call_or_put(self, price, active, action, timeframe):
        return self.instance.buy(price, active, action, timeframe)
    
    def check_win_or_loss(self, id, version):
        
        try:
            if version == 'v3':
                return self.instance.check_win_v3(id)
            if version == 'v4':
                return self.instance.check_win_v4(id)
        except Exception:
            print('version or id is not available')
            
    def call_or_put_digital(self, price, active, action, timeframe):
        return self.instance.buy_digital_spot(active, price, action, timeframe)
    
    def check_win_or_loss_digital(self, id, version='v2'):
        
        try:
            if version == 'v2':
                return self.instance.check_win_digital(id)
        except Exception as error:
            print(f'version error: {error}')
            
    def get_profit(self, active, type):
        return self.instance.get_all_profit()[active][type]
    
    def balance(self, type_balance):
        self.instance.change_balance(type_balance)
        return self.instance.get_balance()
    
    def get_realtime_candles(self, active, size, maxdict):
        self.instance.start_candles_stream(active, size, maxdict)
        candles = self.instance.get_realtime_candles(active, size)
        self.instance.stop_candles_stream(active, size)
        return candles
    
    def call_decision(self, balance, value, active, wins=[], stop_loss=[], active_type=False, payoff=0, goal_win=2, goal_loss=1, account_type=NULL):
        if balance >= value:
            status, id = self.call_or_put(value, active, 'call', 5)
        else:
            print('saldo insuficiente')
            exit()
        
        print(f'compra: R$ {format_currency(value)}')
        
        if status:
            status, check_value = self.check_win_or_loss(id, 'v4')
            
            if status == 'win':
                wins.append(status)
                print(f'total wins: {len(wins)}')
                register_value = value * self.get_profit(active, active_type)
                persist_data(status, active, round(register_value, 2), payoff, account_type)
                
                if len(wins) >= goal_win:
                    print('meta batida')
                    exit()
            else:
                stop_loss.append(status)
                print(f'total loss: {len(stop_loss)}')
                register_value = value
                persist_data(status, active, round(register_value, 2), payoff, account_type)
                
                if len(stop_loss) >= goal_loss:
                    print('stop loss acionado')
                    exit() 
        return status
                    
    def put_decision(self, balance, value, active, wins=[], stop_loss=[], active_type=False, payoff=0, goal_win=2, goal_loss=1, account_type=NULL):
        if balance >= value:
            status, id = self.call_or_put(value, active, 'put', 5)
        else:
            print('saldo insuficiente')
            exit()
        
        print(f'venda: R$ {format_currency(value)}')
        
        if status:
            status, check_value = self.check_win_or_loss(id, 'v4')
            
            if status == 'win':
                wins.append(status)
                print(f'total wins: {len(wins)}')
                register_value = value * self.get_profit(active, active_type)
                persist_data(status, active, round(register_value, 2), payoff, account_type)
                
                if len(wins) >= goal_win:
                    print('meta batida')
                    exit()
                
            else:
                stop_loss.append(status)
                print(f'total loss: {len(stop_loss)}')
                register_value = value
                persist_data(status, active, round(register_value, 2), payoff, account_type)
                
                if len(stop_loss) >= goal_loss:
                    print('stop loss acionado')
                    exit()
        return status
    
    def closest(self, lst, K): 
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
    
    def kelly(self, b, p, q):
        return (b * p - q) / b