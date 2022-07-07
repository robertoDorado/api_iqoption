from iqoptionapi.stable_api import IQ_Option
import time
from datetime import datetime
from pytz import timezone

class BOT_IQ_Option:
    
    def __init__(self):
        self.email = 'robertodorado7@gmail.com'
        self.password = 'Rob@19101910'
        self.instance = IQ_Option(self.email, self.password)
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
    
    def get_all_actives(self):
        return {code:act for act,code in self.instance.get_all_ACTIVES_OPCODE().items()}
    
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
    
    def balance(self):
        return self.instance.get_balance()
    
    def kelly_discretion(self, prob_wins, prob_loss, payoff):
        return (prob_wins * payoff ) - prob_loss / payoff