import time, os
from binance.spot import Spot as Client

api_key = os.getenv('API_KEY')
secret_key = os.getenv('SECRET_KEY')

client = Client(api_key=api_key, api_secret=secret_key, show_limit_usage=True)
account = client.account()['data']
print(account)