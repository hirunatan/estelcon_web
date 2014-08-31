# -*- encoding: utf-8 -*-

from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages

from core import services

from .forms import UserProfileEditPersonalForm, UserProfileEditInscriptionForm

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
        services.change_user_personal_data(self.request.user, form.cleaned_data)
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
        services.change_user_inscription_data(self.request.user, form.cleaned_data)
        messages.info(self.request, u'Datos modificados correctamente')
        return super(UserProfileEditInscriptionView, self).form_valid(form)

