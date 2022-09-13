# Generated by Django 3.2.14 on 2022-08-17 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChainControl', '0025_bank_guid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата договора'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата окончания'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='number',
            field=models.TextField(blank=True, max_length=20, null=True, verbose_name='Номер договора'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата начала'),
        ),
        migrations.AlterField(
            model_name='currency',
            name='code',
            field=models.TextField(blank=True, max_length=3, null=True, verbose_name='Код валюты'),
        ),
        migrations.AlterField(
            model_name='currency',
            name='code_str',
            field=models.TextField(blank=True, max_length=3, null=True, verbose_name='Код валюты строкой'),
        ),
    ]