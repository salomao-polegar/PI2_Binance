# Generated by Django 4.1.7 on 2023-04-15 22:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("binanceapp", "0004_klines_teste"),
    ]

    operations = [
        migrations.AlterField(
            model_name="klines",
            name="close_time",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="klines",
            name="open_time",
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name="klines",
            unique_together={
                (
                    "simbolo",
                    "open_time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "close_time",
                    "interval",
                    "teste",
                )
            },
        ),
    ]
