# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import ScheduleView, ActivityView

urlpatterns = patterns('',
    url(r'^merethaderthad_programa/$', ScheduleView.as_view(), name='schedule'),
    url(r'^merethaderthad_actividad/(?P<activity_id>\d+)/$', ActivityView.as_view(), name='activity'),
)

