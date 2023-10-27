from binanceapp.Client import Client
import pandas as pd
import time, os

class Carteira():
    
    def __init__(self):


        self.client = Client()

        serverTime = int(self.client.time()['data']['serverTime'])
       
        self.account = self.client.account()['data']
        self.balances = pd.DataFrame(self.account['balances'])
        
        self.balances = self.balances[self.balances.free.astype(float) > 0]
        
           #self.wallet =  
        if hasattr(self, 'balances'):
            self.depth()
            self.preenche_dados_carteira()

    def get_carteira(self) -> pd.DataFrame:
        if hasattr(self, 'balances'):
            return self.balances
        else:
            return pd.DataFrame()
    
    def depth(self):
        
        bids, asks = [], []
        for _, v in self.balances.iterrows():
            if v['asset'] == "BRL":
                bids.append(1)
                asks.append(1)
            else:
                symbol = v['asset']+"BRL"
                #print(symbol)
                try:
                    bids.append(self.client.depth(symbol, limit=1)['data']['bids'][0][0])
                    asks.append(self.client.depth(symbol, limit=1)['data']['asks'][0][0])
                except Exception as e:
                    bids.append(0)
                    asks.append(0)
                    print(e)
        
        self.balances['bids'] = [float(x) for x in bids]
        self.balances['asks'] = [float(x) for x in asks]
    
    def preenche_dados_carteira(self):
        self.balances['brlValuation'] = (self.balances['free'].astype(float) * self.balances['bids'])
        self.balances.sort_values(by="brlValuation", inplace=True, ascending=False)
        self.balances['porcentagem'] = (self.balances['brlValuation'].astype(float) / self.balances['brlValuation'].astype(float).sum()) * 100       
        #print(self.balances)     
        self.balances['porcentagem'] = self.balances['porcentagem'].astype(int)
        self.balances = self.balances.reset_index()
        self.balances['index'] = self.balances.index+1

        
        
        