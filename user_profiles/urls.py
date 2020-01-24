from django.conf.urls import url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from .views import (
    PreSignupView, SignupView, SignupExtraView, LoginView, LogoutView, ForgotPasswordView, ChangePasswordView,
    UserProfileView, UserProfileEditPersonalView, UserProfileEditInscriptionView,
    UserListingsIndexView, UserListingView
)

def user_is_staff(user):
    return user.is_staff

if settings.PRE_SIGNUP_FORM:
    # Option initial (pre signup form only send mail to admins, does not create real users)
    urlpatterns = [
        url(r'^inscripcion$', PreSignupView.as_view(),
            name='signup')
    ]
else:
    urlpatterns = [
        url(r'^inscripcion$', SignupView.as_view(),
            name='signup'),
        url(r'^inscripcion-extra$', SignupExtraView.as_view(),
            name='signup')

    ]

urlpatterns += [
    url(r'^entrada$', LoginView.as_view(),
        name='login'),
    url(r'^salida$', LogoutView.as_view(),
        name='logout'),
    url(r'^olvido$', ForgotPasswordView.as_view(),
        name='forgot-password'),
    url(r'^cambiar$', ChangePasswordView.as_view(),
        name='change-password'),
    url(r'^ficha$', login_required(UserProfileView.as_view()),
        name='user-profile'),
    url(r'^ficha-editar-personal$', login_required(UserProfileEditPersonalView.as_view()),
        name='user-profile-edit-personal'),
    url(r'^ficha-editar-inscripcion$', login_required(UserProfileEditInscriptionView.as_view()),
        name='user-profile-edit-inscription'),
    url(r'^listados$', user_passes_test(user_is_staff)(UserListingsIndexView.as_view()),
        name='user-listings-index'),
    url(r'^listados/(?P<listing_id>\d+)$', user_passes_test(user_is_staff)(UserListingView.as_view()),
        name='user-listing'),
]

