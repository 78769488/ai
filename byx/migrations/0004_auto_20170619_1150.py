# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-19 03:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('byx', '0003_auto_20170615_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='dataType',
            field=models.IntegerField(max_length=32, verbose_name='数据类型, 0 :股票 1: 期货'),
        ),
    ]