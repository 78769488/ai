# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-21 04:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('byx', '0006_auto_20170621_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tj',
            name='name',
            field=models.CharField(default=1, max_length=32, verbose_name='上行类别名称'),
            preserve_default=False,
        ),
    ]