# Generated by Django 3.2.14 on 2022-08-07 17:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChainControl', '0013_alter_request_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2022, 8, 7, 23, 26, 4, 377336), verbose_name='Дата создания'),
        ),
    ]