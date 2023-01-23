# Generated by Django 3.2.14 on 2022-11-15 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ChainControl', '0054_alter_request_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ChainControl.client', verbose_name='Контрагент'),
        ),
        migrations.AlterField(
            model_name='request',
            name='invoice_number',
            field=models.CharField(max_length=100, verbose_name='Номер счета на оплату'),
        ),
    ]