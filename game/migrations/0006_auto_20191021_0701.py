# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-21 07:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_sharedpair_game'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sharedpair',
            name='options',
        ),
        migrations.RemoveField(
            model_name='sharedpair',
            name='question',
        ),
        migrations.RemoveField(
            model_name='sharedpair',
            name='selected_answers',
        ),
        migrations.AddField(
            model_name='sharedpair',
            name='sharedplayer1_que_and_ans',
            field=models.CharField(blank=True, max_length=20000),
        ),
        migrations.AddField(
            model_name='sharedpair',
            name='sharedplayer2_que_and_ans',
            field=models.CharField(blank=True, max_length=20000),
        ),
    ]
