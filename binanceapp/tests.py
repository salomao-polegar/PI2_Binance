from django.test import TestCase
import time, requests
from binanceapp.Client import Client

class InternetTest(TestCase):
    def setUp(self):
        self.url = 'https://api.binance.com'

    def testar_conexao_com_internet(self):
        try:
            response_code = requests.get(self.url).status_code
        except Exception as e:
            self.fail(e)

        self.assertEqual(response_code, 200, 
                         f'--> Sem conexão com a internet! Code: {response_code}')

class BinanceTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def testa_hora_servidor(self):
        serverTime = int(self.client.time()['data']['serverTime'])
        localTime = int(time.time()*1000)

        self.assertEqual(serverTime < localTime+1000 and serverTime > localTime-1000, True, 
                         f"\n\n--> A hora do servidor está {serverTime-localTime} ms diferente."+
                         f"\n--> Servidor: {serverTime}"+
                         f"\n--> Local:    {localTime}"+
                         f"\n--> O máximo permitido é 1000 ms.")
        