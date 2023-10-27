from .Client import Client
from binance.error import ClientError
from .enums.interval import Intervalo
from datetime import datetime
from .models import Klines as Klines_DB
import pandas as pd
import numpy as np
import pytz

from .apps import Vars


class Klines():
    
    def __init__(self, simbolo:str, intervalo:Intervalo, limite:int, teste:bool):
        
        try:
            self.client = Client(teste)
        except Exception as e:
            print('ERRO: ', e)

        self.PRECISAO_DECIMAIS = Vars.simbolos[Vars.simbolos.symbol==simbolo]['quotePrecision'].values[0]
        self.quote_asset = Vars.simbolos[Vars.simbolos.symbol==simbolo]['quoteAsset'].values[0]
        self.definir_dados(simbolo, intervalo, limite, teste)

    def get_dados(self) -> pd.DataFrame:
        return self.dados
    
    def definir_dados(self, simbolo:str, intervalo:Intervalo, limite:int, teste:bool) -> pd.DataFrame|None:

        try:
            response = self.client.klines(symbol = simbolo, interval = intervalo, limit = str(limite))
            
            if response == None:
                return None
            dados_web = pd.DataFrame(response['data'])

        
            
        except ClientError as e:
            print("Erro ao acessar os dados da web: ", e)
            try:
                self.dados = pd.DataFrame(Klines_DB.objects.all().values().filter(simbolo = simbolo).order_by('open_time'))
                return self.dados
            
            except KeyError as e:
                if "['id'] not found in axis" in str(e):
                    self.dados=None
                    return None
                else:
                    print("Erro ao acessar banco de dados: ", e)
                    return None
        
        dados_web = dados_web[[0,1,2,3,4,6]]
        alterar = {
            0:"open_time",
            1:"open",
            2:'high',
            3:'low',
            4:'close',
            6:'close_time',
        }
        dados_web = dados_web.rename(columns=alterar).astype(float)

        

        dados_web['interval'] = dados_web['close_time'] - dados_web['open_time']
        dados_web['interval'] = dados_web['interval'].apply(self.calcular_intervalo)
        dados_web['open_time'] = dados_web['open_time'].apply(lambda x: int(x))
        dados_web['close_time'] = dados_web['close_time'].apply(lambda x: int(x))
        dados_web['close_time_utc'] = dados_web['close_time'].apply(lambda x: datetime.fromtimestamp(int(x//1000), tz=pytz.UTC))
        dados_web['open'] = dados_web['open'].apply(lambda x: round(x, self.PRECISAO_DECIMAIS))
        dados_web['close'] = dados_web['close'].apply(lambda x: round(x, self.PRECISAO_DECIMAIS))
        
        dados_web.insert(loc=0, column='simbolo', value = simbolo)
        dados_web['teste'] = teste
        
        dados_web = dados_web[0:-1] # Remove o último registro, visto que ele não foi finalizado ainda (kline em andamento)
        #print("Dados da web")
        #print(dados_web)
                
        #print("Salvando dados no banco...")
        for i, value in dados_web.iterrows():
            
            # : o problema aqui, está duplicando último registro, pois a cada consulta o valor do fechamento muda, já que o dia atual não fechou ainda
            # : resolução: fazer com que o app pule a última iteração
            
            Klines_DB.objects.get_or_create(
                simbolo = value.simbolo,
                open_time = value.open_time,
                open = value.open,
                high = value.high,
                low = value.low,
                close = value.close,
                close_time = value.close_time,
                close_time_utc = value.close_time_utc,
                interval = value.interval,
                teste=teste
            )
            #print(f'{i}/{dados_web.shape[0]}')
        
        # Vai retornar o banco de dados atualizado
        try:
            self.dados = pd.DataFrame(Klines_DB.objects.all().values().filter(simbolo = simbolo).order_by('open_time')).reset_index()
        except KeyError as e:
            pass
        
        
    def calcular_intervalo(self, x:float) -> str:
        """ Recebe um time long e determina qual o intervalo """
        
        segundos = (x+1)/1000
        retorno = ""
        if segundos>=86400: 
            dias = int(np.floor(segundos/86400))
            retorno+=f"{dias}d"
            segundos = segundos%86400
            
        if segundos >= 3600:
            horas = int(np.floor(segundos/3600))
            retorno+=f"{horas}h"
            segundos = segundos%3600
        if segundos >= 60:
            minutos = int(np.floor(segundos/60))
            retorno+=f"{minutos}m"
            segundos = segundos%60
        if segundos > 0:
            retorno+=f"{segundos}s"
        
        return retorno

    def retorna_milissegundos(self, dia:int, mes:int, ano:int) -> int:
        return int(datetime(ano, mes, dia).timestamp()*1000)

    def definir_media(self, dados:pd.DataFrame) -> float:
        
        """A média é a partir do fechamento do período
        Vamos calcular a média de todos os dados recebidos.
        Então, para calcular a média de 10 registros, por exemplo, selecionamos apenas 10 registros do nosso dataframe
        """
        try:
            return dados['close'].mean()
        except AttributeError:
            return dados['close']
        except:
            return 0

    def calcular_media(self, qtde_media:int) -> pd.DataFrame:
        pd.set_option('display.max_columns', None)
        try:
            self.dados = self.dados.reset_index()
        except:
            pass
        media=[]
        
        for indice, _ in self.dados.iterrows():
            if indice+1 >= qtde_media:
                media.append(self.definir_media(self.dados[indice+1-qtde_media: indice]))
            else:
                media.append(0)
        self.dados['media'+str(qtde_media)] = pd.Series(media).apply(lambda x: round(x, self.PRECISAO_DECIMAIS))
    
    def comprar(self, valor:float, custo:float) -> list[float]:
        return [0, valor[0]/custo]

    def vender(self, valor:float, custo:float) -> list[float]:
        return [valor[1]*custo, 0]

    def calcular_porcentagem(self, media:int) -> float:
        # Comprar: quando a média for menor do que tanto a abertura quanto o fechamento
        
        
        
        valor = [100, 0] # BRL | BTC
        close = 0
        
        for _, dado in self.dados.iterrows():

            close = dado['close']

            comprar = (dado['media'+str(media)] < close) & (dado['media'+str(media)] < dado['open'])
            vender  = (dado['media'+str(media)] > close) & (dado['media'+str(media)] > dado['open'])

            
            if comprar == True:
                if valor[0] > 0:
                    valor = self.comprar(valor, close)
            if vender == True:
                if valor[1] > 0:
                    valor = self.vender(valor, close)
        
        if valor[1] > 0:
            valor = self.vender(valor, close)    

        return valor[0]

    
        
        