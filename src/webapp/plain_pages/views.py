# -*- encoding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template.base import TemplateDoesNotExist
from django.http import Http404

def statichtml(request, html_id='index'):
    try:
        return render_to_response('webapp/plain_pages/' + html_id + '.html')
    except TemplateDoesNotExist:
        raise Http404('No se encuentra el documento %s' % html_id)

def statictxt(request, txt_id):
    try:
        return render_to_response(
            'webapp/plain_pages/' + txt_id + '.txt',
            content_type='text/plain'
        )
    except TemplateDoesNotExist:
        raise Http404('No se encuentra el documento %s' % txt_id)

