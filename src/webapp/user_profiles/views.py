# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView

from core.models import Activity

#@login_required
class UserProfileView(TemplateView):
    template_name = 'webapp/user_profiles/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)

        context['profile'] = self.request.user.profile
        context['owner_of'] = Activity.objects.filter(owners__exact = self.request.user)
        context['organizer_of'] = Activity.objects.filter(organizers__exact = self.request.user)
        context['participant_of'] = Activity.objects.filter(participants__exact = self.request.user)
        context['activities_to_participate'] = [
            activity for activity in Activity.objects.filter(requires_inscription__exact = True)
            if not activity in participant_of
        ]

        return context

