# Generated by Django 3.2.14 on 2022-08-04 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ChainControl', '0009_rename_status_request_request_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='request',
            old_name='request_status',
            new_name='status',
        ),
    ]