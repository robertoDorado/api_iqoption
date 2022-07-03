from typing_extensions import Self
from iqoptionapi.stable_api import IQ_Option
import time
from datetime import datetime
from pytz import timezone

class Connection_API_IQ_Option:
    
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
    
    def get_all_candles(self, active='EURUSD', quant=3):
        
        while True:
            try:
                dictionary_actives = self.instance.get_all_ACTIVES_OPCODE()
                for actives in list(dictionary_actives.keys()):
                    if actives == active:
                        return self.instance.get_candles(active, 60, quant, self.current_timestamp)
            except Exception:
                print('is not a valid active')
                break
            
    def get_current_timestamp(self):
        return self.current_timestamp
    
    def convert_timestamp(self, timestamp=time.time(), tz='America/Sao_Paulo'):
        return datetime.fromtimestamp(timestamp, timezone(tz))