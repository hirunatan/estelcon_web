# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.conf import settings

from core import services
from core.models import Activity

from .forms import (
    ActivitySubscribeForm, ProposalForm
)


class ScheduleView(TemplateView):
    template_name = 'webapp/activities/schedule.html'


class ScheduleDevelView(TemplateView):
    template_name = 'webapp/activities/schedule_devel.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduleDevelView, self).get_context_data(**kwargs)
        (activ_without_hour, days) = services.get_schedule()
        context['activ_without_hour'] = activ_without_hour
        context['days'] = days
        return context


class ActivityView(TemplateView):
    template_name = 'webapp/activities/activity.html'

    def get(self, request, *args, **kwargs):
        (self.activity, self.user_status) = services.get_activity_and_status(kwargs['activity_id'], self.request.user)
        return super(ActivityView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ActivityView, self).get_context_data(**kwargs)

        context['activity'] = self.activity
        if self.activity:
            context['is_owner'] = self.user_status['is_owner']
            context['is_organizer'] = self.user_status['is_organizer']
            context['is_participant'] = self.user_status['is_participant']
            context['is_admin'] = self.user_status['is_admin']

        return context


class ActivitySubscribeView(FormView):
    template_name = 'webapp/activities/activity_subscribe.html'
    form_class = ActivitySubscribeForm
    success_url = reverse_lazy('user-profile')

    def dispatch(self, request, *args, **kwargs):
        (self.activity, self.user_status) = services.get_activity_and_status(kwargs['activity_id'], self.request.user)
        return super(ActivitySubscribeView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            'id': self.activity.id if self.activity else 0,
            'title': self.activity.title if self.activity else '',
        }

    def get_context_data(self, **kwargs):
        context = super(ActivitySubscribeView, self).get_context_data(**kwargs)

        if self.activity \
                and self.activity.requires_inscription \
                and not self.user_status['is_owner'] \
                and not self.user_status['is_organizer'] \
                and not self.user_status['is_participant']:
            context['activity'] = self.activity
        else:
            context['activity'] = None

        return context

    def form_valid(self, form):
        services.subscribe_to_activity(
            user = self.request.user,
            activity_id = form.cleaned_data['id'],
        )
        messages.info(self.request, u'Te has inscrito en la actividad.')
        return super(ActivitySubscribeView, self).form_valid(form)


class ActivityEditView(UpdateView):
    template_name = 'webapp/activities/activity_edit.html'
    model = Activity
    pk_url_kwarg = 'activity_id'
    fields = ['id', 'title', 'subtitle', 'duration', 'max_places', 'show_owners', 'text', 'logistics', 'notes_organization']

    def form_valid(self, form):
        result = super(ActivityEditView, self).form_valid(form)
        services.change_activity(
            user = self.request.user,
            activity = self.object,
            home_url = settings.PROTOCOL + '://' + settings.SITE_URL,
        )
        messages.info(self.request, u'Datos modificados correctamente')
        return result

    def get_success_url(self):
        return reverse_lazy('activity', args=[self.object.id])


class ProposalSentView(TemplateView):
    template_name = 'webapp/activities/proposal_sent.html'


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


