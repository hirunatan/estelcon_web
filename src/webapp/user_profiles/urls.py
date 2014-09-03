# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (
    SignupView, LoginView, LogoutView, ForgotPasswordView, ChangePasswordView,
    UserProfileView, UserProfileEditPersonalView, UserProfileEditInscriptionView
)

urlpatterns = patterns('',
    url(r'^merethaderthad_inscripcion/$', SignupView.as_view(),
        name='login'),
    url(r'^merethaderthad_entrada/$', LoginView.as_view(),
        name='login'),
    url(r'^merethaderthad_salida/$', LogoutView.as_view(),
        name='logout'),
    url(r'^merethaderthad_olvido/$', ForgotPasswordView.as_view(),
        name='forgot-password'),
    url(r'^merethaderthad_cambiar/$', ChangePasswordView.as_view(),
        name='change-password'),
    url(r'^merethaderthad_ficha/$', login_required(UserProfileView.as_view()),
        name='user-profile'),
    url(r'^merethaderthad_ficha_editar_pers/$', login_required(UserProfileEditPersonalView.as_view()),
        name='user-profile-edit-personal'),
    url(r'^merethaderthad_ficha_editar_inscr/$', login_required(UserProfileEditInscriptionView.as_view()),
        name='user-profile-edit-inscription'),
)

