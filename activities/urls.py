from django.conf.urls import url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from .views import (
    ScheduleHiddenView, ScheduleRealView, ActivityView, ActivitySubscribeView, ActivityEditView, ProposalView, ProposalSentView
)


def user_is_staff(user):
    return user.is_staff


if settings.SCHEDULE_HIDDEN:
    urlpatterns = [
        # Option initial (schedule is hidden, visible only to admin)
        url(r'^mereth-aderthad/programa/$', ScheduleHiddenView.as_view(), name='schedule'),
        url(r'^mereth-aderthad/programa-desarrollo/$', user_passes_test(user_is_staff)(ScheduleRealView.as_view()), name='schedule-devel'),
    ]
else:
    urlpatterns = [
        # Option normal (schedule is publicly visible)
        url(r'^mereth-aderthad/programa/$', ScheduleRealView.as_view(), name='schedule'),
    ]

urlpatterns += [
    url(r'^mereth-aderthad/actividad/(?P<activity_id>\d+)/$', ActivityView.as_view(), name='activity'),
    url(r'^mereth-aderthad/actividad-inscribir/(?P<activity_id>\d+)/$', login_required(ActivitySubscribeView.as_view()), name='activity-subscribe'),
    url(r'^mereth-aderthad/actividad-editar/(?P<activity_id>\d+)/$', login_required(ActivityEditView.as_view()), name='activity-edit'),
    url(r'^mereth-aderthad/propuesta/$', login_required(ProposalView.as_view()), name='proposal'),
    url(r'^mereth-aderthad/propuesta-enviada/$', login_required(ProposalSentView.as_view()), name='proposal-sent'),
]

