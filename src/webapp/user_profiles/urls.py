# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import UserProfileView, UserProfileEditPersonalView

urlpatterns = patterns('',
    url(r'^merethaderthad_ficha/$', UserProfileView.as_view(), name='user-profile'),
    url(r'^merethaderthad_ficha_editar_pers/$', UserProfileEditPersonalView.as_view(), name='user-profile-edit-personal'),
)

