# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import LoginView, UserProfileView, UserProfileEditPersonalView, UserProfileEditInscriptionView

urlpatterns = patterns('',
    url(r'^merethaderthad_entrada/$', LoginView.as_view(),
        name='login'),
    url(r'^merethaderthad_ficha/$', login_required(UserProfileView.as_view()),
        name='user-profile'),
    url(r'^merethaderthad_ficha_editar_pers/$', login_required(UserProfileEditPersonalView.as_view()),
        name='user-profile-edit-personal'),
    url(r'^merethaderthad_ficha_editar_inscr/$', login_required(UserProfileEditInscriptionView.as_view()),
        name='user-profile-edit-inscription'),
)

