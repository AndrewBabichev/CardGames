# Generated by Django 3.0.4 on 2021-05-21 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_room_n_ready'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='n_free',
            field=models.IntegerField(default=0),
        ),
    ]