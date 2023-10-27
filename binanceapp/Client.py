from binance.spot import Spot
from dotenv import load_dotenv
import os, time



class Vars(object):
    simbolos = None
    limites = None
    limiteIPUtilizado = 0 # current used weight for the IP for all request rate limiters defined
    limitOrder = 0 # the current order count for the account for all order rate limiters defined
    teste = False

class Client(Spot):
    
    def __init__(self, teste:bool=Vars.teste):
        
        self.time_offset = 0

        

        load_dotenv()




        try:
            if teste:
                api_key = os.getenv('API_KEY_TESTE')
                secret_key = os.getenv('SECRET_KEY_TESTE')
                super().__init__(api_key=api_key, api_secret=secret_key, base_url='https://testnet.binance.vision',  show_limit_usage=True)
            else:
                api_key = os.getenv('API_KEY')
                secret_key = os.getenv('SECRET_KEY')
                super().__init__(api_key=api_key, api_secret=secret_key, show_limit_usage=True)
        except Exception as e:
            print(e)
