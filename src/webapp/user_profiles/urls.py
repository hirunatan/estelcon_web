# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import UserProfileView

urlpatterns = patterns('',
    url(r'^merethaderthad_ficha/$', UserProfileView.as_view(), name='user-profile'),
)

