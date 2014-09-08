# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.conf import settings

from core import services

from .forms import (
    ProposalForm
)


class ScheduleView(TemplateView):
    template_name = 'webapp/activities/schedule.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        (activ_without_hour, days) = services.get_schedule()
        context['activ_without_hour'] = activ_without_hour
        context['days'] = days
        return context


class ActivityView(TemplateView):
    template_name = 'webapp/activities/activity.html'

    def get_context_data(self, **kwargs):
        context = super(ActivityView, self).get_context_data(**kwargs)

        (activity, user_status) = services.get_activity_and_status(self.activity_id, self.request.user)
        context['activity'] = activity
        if activity:
            context['is_owner'] = user_status['is_owner']
            context['is_organizer'] = user_status['is_organizer']
            context['is_participant'] = user_status['is_participant']
            context['is_admin'] = user_status['is_admin']

        return context

    def get(self, request, *args, **kwargs):
        self.activity_id = kwargs['activity_id']
        return super(ActivityView, self).get(request, *args, **kwargs)


class ProposalView(FormView):
    template_name = 'webapp/activities/proposal.html'
    form_class = ProposalForm
    success_url = reverse_lazy('proposal-sent')

    def form_valid(self, form):
        services.send_proposal(
            user = self.request.user,
            data = form.cleaned_data,
            home_url = settings.PROTOCOL + '://' + settings.SITE_URL,
        )
        messages.info(self.request, u'Se ha enviado la propuesta a los organizadores.')
        return super(ProposalView, self).form_valid(form)


class ProposalSentView(TemplateView):
    template_name = 'webapp/activities/proposal_sent.html'


