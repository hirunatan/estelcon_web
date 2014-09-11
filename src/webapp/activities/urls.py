# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (
    ScheduleView, ActivityView, ActivitySubscribeView, ActivityEditView, ProposalView, ProposalSentView
)

urlpatterns = patterns('',
    url(r'^merethaderthad_programa/$', ScheduleView.as_view(), name='schedule'),
    url(r'^merethaderthad_actividad/(?P<activity_id>\d+)/$', ActivityView.as_view(), name='activity'),
    url(r'^merethaderthad_actividad_inscribir/(?P<activity_id>\d+)/$', login_required(ActivitySubscribeView.as_view()), name='activity-subscribe'),
    url(r'^merethaderthad_actividad_editar/(?P<activity_id>\d+)/$', login_required(ActivityEditView.as_view()), name='activity-edit'),
    url(r'^merethaderthad_propuesta/$', login_required(ProposalView.as_view()), name='proposal'),
    url(r'^merethaderthad_propuesta_enviada/$', login_required(ProposalSentView.as_view()), name='proposal-sent'),
)

