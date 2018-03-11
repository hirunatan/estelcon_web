# -*- encoding: utf-8 -*-

from django.shortcuts import render_to_response
# from django.template.base import TemplateDoesNotExist
from django.template import RequestContext
from django.http import Http404

def statichtml(request, html_id='index'):
    # try:
        return render_to_response(
            'webapp/plain_pages/' + html_id + '.html',
            context = RequestContext(request),
        )
    # except TemplateDoesNotExist:
    #     raise Http404('No se encuentra el documento %s' % html_id)

