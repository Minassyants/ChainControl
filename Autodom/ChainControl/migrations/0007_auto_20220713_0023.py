# Generated by Django 2.2.28 on 2022-07-12 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ChainControl', '0006_auto_20220712_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='request_type',
            name='executor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='role_executor', to='ChainControl.Role'),
        ),
        migrations.AddField(
            model_name='request_type',
            name='initiator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='role_initiator', to='ChainControl.Role'),
        ),
    ]
