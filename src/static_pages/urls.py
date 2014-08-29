from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^(?P<html_id>.*).html$','static_pages.views.statichtml'),
    (r'^$', 'static_pages.views.statichtml'),
)
