# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from .views import (
    ScheduleHiddenView, ScheduleRealView, ActivityView, ActivitySubscribeView, ActivityEditView, ProposalView, ProposalSentView
)


def user_is_staff(user):
    return user.is_staff


if settings.SCHEDULE_HIDDEN:
    urlpatterns = patterns('',
        # Option initial (schedule is hidden, visible only to admin)
        url(r'^merethaderthad_programa/$', ScheduleHiddenView.as_view(), name='schedule'),
        url(r'^merethaderthad_programa_desarrollo/$', user_passes_test(user_is_staff)(ScheduleRealView.as_view()), name='schedule-devel'),
    )
else:
    urlpatterns = patterns('',
        # Option normal (schedule is publicly visible)
        url(r'^merethaderthad_programa/$', ScheduleRealView.as_view(), name='schedule'),
    )

urlpatterns += patterns('',
    url(r'^merethaderthad_actividad/(?P<activity_id>\d+)/$', ActivityView.as_view(), name='activity'),
    url(r'^merethaderthad_actividad_inscribir/(?P<activity_id>\d+)/$', login_required(ActivitySubscribeView.as_view()), name='activity-subscribe'),
    url(r'^merethaderthad_actividad_editar/(?P<activity_id>\d+)/$', login_required(ActivityEditView.as_view()), name='activity-edit'),
    url(r'^merethaderthad_propuesta/$', login_required(ProposalView.as_view()), name='proposal'),
    url(r'^merethaderthad_propuesta_enviada/$', login_required(ProposalSentView.as_view()), name='proposal-sent'),
)

