# _*_ coding: utf-8 _*_
from iqoption.connection import BOT_IQ_Option
from random import choices
from datetime import datetime

account_type = "PRACTICE"
API = BOT_IQ_Option(account_type)

if API.check_my_connection() == False:
    print('erro na conexão')
    exit()

balance = API.balance(account_type)
print(f'my account is {account_type}: R$ {balance}')


while True:
    
    try:
        name = ''
    except Exception as error:
        print(f'something wrong: {error}')