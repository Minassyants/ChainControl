# Generated by Django 3.2.14 on 2022-09-16 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChainControl', '0031_auto_20220916_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email_templates',
            name='tg_text',
            field=models.TextField(default='123', max_length=400, verbose_name='Текст телеграмм сообщения'),
        ),
    ]