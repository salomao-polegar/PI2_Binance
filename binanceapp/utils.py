from django.shortcuts import render
from datetime import datetime
import time
import pandas as pd
from binance.spot import Spot as Client
from binance.error import ClientError
import numpy as np
from .models import Klines
import os
from .enums.interval import Intervalo
#import logging

def formatarMoeda(n:str|float|int, sufixo:str = None):
    n=str(np.format_float_positional(float(n)))
    text=''
    virgula=''
    index_ponto = n.find('.')

    for i in range(0, index_ponto):
        text+=n[i]
        resto = index_ponto-i-1
        if resto % 3 == 0 and resto != 0:            
            text+='.'
    if index_ponto != len(n)-1:
        virgula = ','
    return text+virgula+n[index_ponto+1:]+' '+sufixo