# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages

from core import services

class ScheduleView(TemplateView):
    template_name = 'webapp/activities/schedule.html'

    def get_context_data(self, **kwargs):
        context = super(ScheduleView, self).get_context_data(**kwargs)
        (activ_without_hour, days) = services.get_schedule()
        context['activ_without_hour'] = activ_without_hour
        context['days'] = days
        return context

