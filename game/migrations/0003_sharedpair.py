# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-20 09:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_participants_searching_pair'),
        ('game', '0002_auto_20191018_2036'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedPair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_pair', models.BooleanField(default=False)),
                ('sharedplayer1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sharedplayer1', to='account.Participants')),
                ('sharedplayer2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sharedplayer2', to='account.Participants')),
            ],
        ),
    ]
