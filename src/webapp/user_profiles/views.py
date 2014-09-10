# -*- encoding: utf-8 -*-

from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.conf import settings

from core import services

from .forms import (
    SignupForm, LoginForm, ForgotPasswordForm, ChangePasswordForm,
    UserProfileEditPersonalForm, UserProfileEditInscriptionForm
)


class SignupView(FormView):
    template_name = 'webapp/user_profiles/signup.html'
    form_class = SignupForm

    def form_valid(self, form):
        (user, queue) = services.create_new_user(
            user_data = form.cleaned_data,
            home_url = settings.PROTOCOL + '://' + settings.SITE_URL,
        )
        self.user = user
        self.queue = queue
        return super(SignupView, self).form_valid(form)

    def get_success_url(self):
        profile = self.user.profile
        return reverse('login') + '?payment_code=%s&quota=%d&queue=%d' % (
            profile.payment_code,
            profile.quota,
            self.queue,
        )


class LoginView(FormView):
    template_name = 'webapp/user_profiles/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('user-profile')

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)

        context['payment_code'] = self.request.GET.get('payment_code', '')
        context['quota'] = self.request.GET.get('quota', 0)
        try:
            context['queue'] = int(self.request.GET.get('queue', 0))
        except ValueError:
            context['queue'] = 0

        return context

    def form_valid(self, form):
        login(self.request, form.cleaned_data['user'])
        return super(LoginView, self).form_valid(form)


class LogoutView(TemplateView):
    template_name = 'webapp/user_profiles/logout.html'

    def get(self, *args, **kwargs):
        logout(self.request)
        return super(LogoutView, self).get(*args, **kwargs)


class ForgotPasswordView(FormView):
    template_name = 'webapp/user_profiles/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('forgot-password')

    def form_valid(self, form):
        services.send_password_reminder(
            user = form.cleaned_data['user'],
            change_password_url_pattern = settings.PROTOCOL + '://' + settings.SITE_URL +
                reverse('change-password') + '?reminder_code=%s',
        )
        messages.info(self.request, u'Se ha enviado a tu dirección de correo un mensaje con instrucciones para crear una nueva contraseña.')
        return super(ForgotPasswordView, self).form_valid(form)


class ChangePasswordView(FormView):
    template_name = 'webapp/user_profiles/change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('user-profile')

    def get_initial(self):
        return {
            'reminder_code': self.request.GET.get('reminder_code', '')
        }

    def form_valid(self, form):
        services.change_user_password(
            user = form.cleaned_data['user'],
            password = form.cleaned_data['password1']
        )
        messages.info(self.request, u'Tu contraseña ha sido cambiada. Ya puedes entrar con ella.')
        return super(ChangePasswordView, self).form_valid(form)


class UserProfileView(TemplateView):
    template_name = 'webapp/user_profiles/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)

        user = self.request.user
        context['profile'] = user.profile
        context['owned_by'] = services.get_activities_owned_by(user)
        context['organized_by'] = services.get_activities_organized_by(user)
        context['participant_in'] = services.get_activities_in_which_participates(user)
        context['activities_to_participate'] = services.get_activities_to_participate_by(user)

        return context


class UserProfileEditPersonalView(FormView):
    template_name = 'webapp/user_profiles/user_profile_edit_personal.html'
    form_class = UserProfileEditPersonalForm
    success_url = reverse_lazy('user-profile')

    def get_initial(self):
        user = self.request.user
        profile = user.profile
        return {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'alias': profile.alias,
            'smial': profile.smial,
            'phone': profile.phone,
            'city': profile.city,
            'age': profile.age,
        }

    def form_valid(self, form):
        services.change_user_personal_data(
            user = self.request.user,
            new_data = form.cleaned_data,
            home_url = settings.PROTOCOL + '://' + settings.SITE_URL,
        )
        messages.info(self.request, u'Datos modificados correctamente')
        return super(UserProfileEditPersonalView, self).form_valid(form)


class UserProfileEditInscriptionView(FormView):
    template_name = 'webapp/user_profiles/user_profile_edit_inscription.html'
    form_class = UserProfileEditInscriptionForm
    success_url = reverse_lazy('user-profile')

    def get_initial(self):
        user = self.request.user
        profile = user.profile
        return {
            'notes_food': profile.notes_food,
            'notes_transport': profile.notes_transport,
            'notes_general': profile.notes_general,
            'dinner_menu': profile.dinner_menu,
            'shirts_S': profile.shirts_S,
            'shirts_M': profile.shirts_M,
            'shirts_L': profile.shirts_L,
            'shirts_XL': profile.shirts_XL,
            'shirts_XXL': profile.shirts_XXL
        }

    def form_valid(self, form):
        services.change_user_inscription_data(
            user = self.request.user,
            new_data = form.cleaned_data,
            home_url = settings.PROTOCOL + '://' + settings.SITE_URL,
        )
        messages.info(self.request, u'Datos modificados correctamente')
        return super(UserProfileEditInscriptionView, self).form_valid(form)

