# Generated by Django 3.2.14 on 2022-08-17 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChainControl', '0024_currency_guid'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='guid',
            field=models.TextField(default=123, max_length=36, verbose_name='ГУИД 1с'),
            preserve_default=False,
        ),
    ]
