# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import statichtml

urlpatterns = patterns('',
    url(r'^(?P<html_id>.*).html$', statichtml),
    url(r'^$', statichtml),
)
