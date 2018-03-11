# -*- encoding: utf-8 -*-

from django.conf.urls import url

from .views import statichtml

urlpatterns = [
    url(r'^(?P<html_id>.*).html$', statichtml),
    url(r'^$', statichtml),
]
