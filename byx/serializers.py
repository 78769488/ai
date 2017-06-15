#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "ZhangRF"
# Date: 2017/6/8

from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializers(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        # 显示字段
        fields = ('url', 'name')