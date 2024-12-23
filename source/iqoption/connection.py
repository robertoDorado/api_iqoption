from iqoptionapi.stable_api import IQ_Option
import time
from components.helpers import *
from scipy.stats import norm
from scipy import stats


class BOT_IQ_Option:

    def __init__(self, account_type, email, password):
        self.email = email
        self.password = password
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

    def set_time_sleep(self, value):
        return time.sleep(value)

    def get_ticks_real_time(self, active='EURUSD', size=60, maxdict=1):

        self.instance.start_candles_stream(active, size, maxdict)
        ticks = self.instance.get_realtime_candles(active, size)

        self.instance.stop_candles_stream(active, size)
        return ticks

    def get_all_actives(self, act=True):

        if act:
            return {code: act for act, code in self.instance.get_all_ACTIVES_OPCODE().items()}
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
        return list(candles.values())

    def call_decision(self, index_iter=0, current_index=1, active_index=[], value=2, active='EURUSD', account_type='PRACTICE', timestamp=5, wins=[], loss=[]):
        if self.balance(account_type) >= value:
            status, id = self.call_or_put(value, active, 'call', timestamp)
        else:
            print('saldo insuficiente')
            exit()

        if status:
            print(f'compra: {format_currency(value)}')
            status_check, check_value = self.check_win_or_loss(id, 'v4')

            if status_check == 'win':
                wins.append(status_check)
                print(f'Win: {len(wins)}')
            else:
                loss.append(status_check)
                print(f'Loss: {len(loss)}')
        else:
            status = False
            status_check = ''
            print(f'ativo {active} indisponivel')
            index_iter = remove_index(current_index, active_index)

        return status, status_check, active, current_index, index_iter, wins, loss

    def put_decision(self, index_iter=0, current_index=1, active_index=[], value=2, active='EURUSD', account_type='PRACTICE', timestamp=5, wins=[], loss=[]):
        if self.balance(account_type) >= value:
            status, id = self.call_or_put(value, active, 'put', timestamp)
        else:
            print('saldo insuficiente')
            exit()

        if status:
            print(f'venda: {format_currency(value)}')
            status_check, check_value = self.check_win_or_loss(id, 'v4')

            if status_check == 'win':
                wins.append(status_check)
                print(f'Win: {len(wins)}')
            else:
                loss.append(status_check)
                print(f'Loss: {len(loss)}')
        else:
            status = False
            status_check = ''
            print(f'ativo {active} indisponivel')
            index_iter = remove_index(current_index, active_index)

        return status, status_check, active, current_index, index_iter, wins, loss

    def change_active(self, index_iter, active_type):
        current_index = next(index_iter)
        actives_open = self.instance.get_all_open_time()

        actives_open = [active for active, info in actives_open[active_type].items() if info['open'] == True]
        actives_open = list(map(lambda x: x.replace("-op", ""), actives_open))

        active = self.get_all_actives()
        active = {k: v for k, v in active.items() if v in actives_open}
        return active[current_index], current_index
    
    def calculate_stop_loss(self, balance, rate_stop_loss):
        return balance - (balance * rate_stop_loss)
    
    def calculate_goal(self, balance, rate_goal):
        return balance + (balance * rate_goal)
    
    def normal_distribution(self, mean, std, value, param):
        z = (value - mean) / std
        return norm.sf(z) if param == 'High' else norm.cdf(z) if param == 'Low' else None
    
    def shap(self, data):
        return stats.shapiro(data)
    
    def probability_on_input(self, probability, account_type):
        if probability >= 50 and probability <= 60:
            return float(format(self.balance(account_type) * 0.05, '.2f'))
        elif probability >= 60:
            return float(format(self.balance(account_type) * 0.1, '.2f'))
        else:
            return 5
            
