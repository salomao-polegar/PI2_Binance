from django.db import models

# Create your models here.
class Klines(models.Model):
    """
        Armazena os dados do gráfico de velas
    """
    simbolo = models.CharField(max_length=20)
    open_time = models.IntegerField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    close_time = models.IntegerField()
    close_time_utc = models.DateTimeField()
    interval = models.CharField(max_length=30)
    teste = models.BooleanField()
    
    class Meta:
        unique_together = ['simbolo', 'open_time', 'open', 'high', 'low', 'close', 'close_time', 'interval', 'teste', 'close_time_utc']
    
    
class Media(models.Model):
    """ para cada kline, uma média de n dias diferente"""
    kline = models.ForeignKey(Klines, models.CASCADE)
    quantidade_media = models.IntegerField()    
    
    
    
    