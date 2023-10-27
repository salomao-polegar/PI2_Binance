from django.shortcuts import render
from .Klines import Klines
from .Carteira import Carteira
import pandas as pd
from django.shortcuts import render
from .apps import Vars
from .enums.interval import Intervalo
import numpy as np
from binance.error import ClientError

# Create your views here.

def index(request):
    simbolo='BTCBRL'
    intervalo = Intervalo._1DIA
    limite = 50
    media = 7
    media2 = 10
    teste = Vars.teste


    if request.method == 'POST':
        simbolo = request.POST.get("par", simbolo)
        intervalo = request.POST.get("intervalo", intervalo)
        intervalo = Intervalo(intervalo)
        limite = int(request.POST.get("velas", limite))
        teste = bool(request.POST.get("teste", teste))
        media = int(request.POST.get("media", media))
        media2 = int(request.POST.get('media2', media2))+1
    
    print(simbolo)
    
    if simbolo.upper == 'BRLBRL':
        simbolo = 'BTCBRL'

    simbolos = Vars.simbolos.symbol.to_list()
    intervalos = [i for i in Intervalo]
    
    klines = Klines(simbolo=simbolo, intervalo=intervalo.value, limite=limite+media2, teste=teste)
    
    
    porcentagem = []
    if media2:
        for i in range(media, int(media2)):
            #print('media',i)
            klines.calcular_media(i)
            porcentagem.append([i, klines.calcular_porcentagem(i), f'{limite}x{intervalo.value}'])
    else:
        klines.calcular_media(media)

    porcentagem = pd.DataFrame(porcentagem, columns=["numero", 'porcentagem', 'periodo'])
    porcentagem = porcentagem.sort_values(by=['porcentagem'], ascending=False)
    porcentagem['numero'] = porcentagem['numero'].astype(int)
    porcentagem['porcentagem2'] = porcentagem['porcentagem'].apply(lambda x: f'{(x-100):.2f}%')
    
    porcentagem = porcentagem.values.tolist()
   
    preloader = """  

    """

    context = {
        "simboloGrafico" : simbolo,
        "simbolos" : simbolos,
        "klines" : plotar_grafico_js(klines, media, limite),
        'intervalos' : intervalos,
        'intervaloGrafico' : intervalo,
        'velas' : limite,
        'medias' : [media, media2],
        'porcentagens' : porcentagem,
        'preloader': preloader
    }
        
    return render(request, 'AdminLTE/index.html', context=context)


def carteira(request):
    try:
        carteira = Carteira()
        dadosCarteira = carteira.get_carteira()
        #print(dadosCarteira)
        dadosCarteira=dadosCarteira[dadosCarteira['brlValuation'] != 0]
        context = {
            'carteira' : dadosCarteira.to_dict('records')
        }
    except ClientError as e:
        print(e)
        context = {}
    
    
    

    return render(request, 'AdminLTE/carteira.html', context=context)

















def plotar_grafico_js(klines:Klines, media:int, limite:int):
    dados_klines = klines.get_dados().tail(limite)
    #print(dados_klines)

    texto = """
    let media;
    let currency = {style: 'currency', currency: '"""
    texto += klines.quote_asset
    texto += """'};
    var options = {
        series: [{
        name: 'line',
        type: 'line',
        data: ["""
    for _, kline in dados_klines.iterrows():
        if float(kline['media'+str(media)]) != 0:
            texto+=("\n            {\n"
f"                x: new Date({kline['open_time']}),\n"
f"                y: '{np.format_float_positional(kline['media'+str(media)])}' \n"
"            },")
       

    texto+="""]
    }, {
      name: 'candle',
      type: 'candlestick',
      data: ["""
    
    for _, kline in dados_klines.iterrows():
        texto+=("{\n"
            f"x: new Date({kline['open_time']}),\n"
#            f"y: [{kline['open']}, {kline['high']}, {kline['low']}, {kline['close']}]\n"
            f"y: [{np.format_float_positional(kline['open'])}, {np.format_float_positional(kline['high'])}, {np.format_float_positional(kline['low'])}, {np.format_float_positional(kline['close'])}]\n"
        "},\n")
        
        
    texto+="""]
        }],
        chart: {
        height: 350,
        type: 'line',
        },
        title: {
        text: 'Gráfico de Velas',
        align: 'left'
        },
        stroke: {
        width: [3, 1]
        },
        tooltip: {
        shared: true,
        custom: function({ seriesIndex, dataPointIndex, w }) {
            var o = w.globals.seriesCandleO[seriesIndex][dataPointIndex];
            var h = w.globals.seriesCandleH[seriesIndex][dataPointIndex];
            var l = w.globals.seriesCandleL[seriesIndex][dataPointIndex];
            var c = w.globals.seriesCandleC[seriesIndex][dataPointIndex];
            media = w.globals.series[0][dataPointIndex];
            return (
            '<div class="callout callout-info" style="background-color: #cadbeb;margin:0rem">' +
              '<div><b>Abertura:</b> <span class="value">' +
              o +
              '</span></div>' +
              '<div><b>Máximo:</b> <span class="value">' +
              h +
              '</span></div>' +
              '<div><b>Mínimo:</b> <span class="value">' +
              l +
              '</span></div>' +
              '<div><b>Fechamento:</b> <span class="value">' +
              c +
              '</span></div>' +
              '<div><b>Média """
    texto+=str(media)
    texto += """ dias:</b> <span class="value">' +
              media +
              '</span></div>' +
              '</div>'
            )
        }
        },
        xaxis: {
        type: 'datetime'
        }
        };

        var chart = new ApexCharts(document.querySelector("#chart"), options);
        chart.render();
        """
    
    with open('graficoJS.js', 'w') as file:
        file.write(texto)

    return texto