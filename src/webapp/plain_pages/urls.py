from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^(?P<html_id>.*).html$','webapp.plain_pages.views.statichtml'),
    (r'^$', 'webapp.plain_pages.views.statichtml'),
)
