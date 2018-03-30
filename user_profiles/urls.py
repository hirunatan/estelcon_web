from django.conf.urls import url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from .views import (
    PreSignupView, SignupView, LoginView, LogoutView, ForgotPasswordView, ChangePasswordView,
    UserProfileView, UserProfileEditPersonalView, UserProfileEditInscriptionView,
    UserListingsIndexView, UserListingView
)

def user_is_staff(user):
    return user.is_staff

if settings.PRE_SIGNUP_FORM:
    # Option initial (pre signup form only send mail to admins, does not create real users)
    urlpatterns = [
        url(r'^mereth-aderthad/inscripcion/$', PreSignupView.as_view(),
            name='signup')
    ]
else:
    urlpatterns = [
        url(r'^mereth-aderthad/inscripcion/$', SignupView.as_view(),
            name='signup')
    ]

urlpatterns += [
    url(r'^mereth-aderthad/entrada/$', LoginView.as_view(),
        name='login'),
    url(r'^mereth-aderthad/salida/$', LogoutView.as_view(),
        name='logout'),
    url(r'^mereth-aderthad/olvido/$', ForgotPasswordView.as_view(),
        name='forgot-password'),
    url(r'^mereth-aderthad/cambiar/$', ChangePasswordView.as_view(),
        name='change-password'),
    url(r'^mereth-aderthad/ficha/$', login_required(UserProfileView.as_view()),
        name='user-profile'),
    url(r'^mereth-aderthad/ficha-editar-personal/$', login_required(UserProfileEditPersonalView.as_view()),
        name='user-profile-edit-personal'),
    url(r'^mereth-aderthad/ficha-editar-inscripcion/$', login_required(UserProfileEditInscriptionView.as_view()),
        name='user-profile-edit-inscription'),
    url(r'^listados/$', user_passes_test(user_is_staff)(UserListingsIndexView.as_view()),
        name='user-listings-index'),
    url(r'^listados/(?P<listing_id>\d+)/$', user_passes_test(user_is_staff)(UserListingView.as_view()),
        name='user-listing'),
]

