#_*_ coding: utf-8 _*_
from iqoption.connection import Connection_API_IQ_Option

API = Connection_API_IQ_Option()

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

instance = API.get_instance()
print(API.convert_timestamp())
# print(instance.get_digital_payout('EURUSD'))