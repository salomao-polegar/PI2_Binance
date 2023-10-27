from django.apps import AppConfig
import pandas as pd
from .Client import Client, Vars
import sys

TESTING = sys.argv[1:2] == ['test']

class BinanceappConfig(AppConfig):

    

    default_auto_field = "django.db.models.BigAutoField"
    name = "binanceapp"
    
    def ready(self):
        # Script de inicialização
        # Para executar sem duplicar o script, é necessário na execução:
        # python manage.py runserver --noreload
        
        if not TESTING:
            
            params = {
                'permissions' : ['SPOT'],
            }
            
            client = Client()
            response = client.exchange_info()['data']
            symbols = pd.DataFrame(response['symbols'])[['symbol', 'status', 'baseAsset', 'quoteAsset', 'quotePrecision']]
            rateLimits = pd.DataFrame(response['rateLimits'])
            
            rateLimits.index=rateLimits['rateLimitType'].values + '_' + rateLimits['interval'].values
            rateLimits = rateLimits.drop(['rateLimitType'], axis=1)

            Vars.limites = rateLimits
            Vars.simbolos = symbols
            #print (Vars.simbolos)
            #logger.info("RateLimits: \n",rateLimits)



    