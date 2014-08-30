# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView

from core import services

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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfileView, self).dispatch(*args, **kwargs)

