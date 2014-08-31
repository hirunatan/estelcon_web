# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import ScheduleView

urlpatterns = patterns('',
    url(r'^merethaderthad_programa/$', ScheduleView.as_view(), name='schedule'),
)

