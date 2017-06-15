#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "ZhangRF"
# Date: 2017/6/8

from django.conf.urls import url, include
# from rest_framework import routers
from byx import views


# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

# Wite up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.

urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'query', views.query),
    url(r'^', views.index),
    # 验证登录使用
    url(r'auth', include('rest_framework.urls'))
]