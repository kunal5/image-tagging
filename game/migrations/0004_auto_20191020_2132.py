# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-20 21:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_sharedpair'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharedpair',
            name='options',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='sharedpair',
            name='question',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='sharedpair',
            name='selected_answers',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
