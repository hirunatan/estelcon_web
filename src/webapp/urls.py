# -*- encoding: utf-8 -*-

import django

from django.conf.urls import include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url('admin/', admin.site.urls),
    url('', include('webapp.user_profiles.urls')),
    url('', include('webapp.activities.urls')),
    url('', include('webapp.plain_pages.urls')),
]

# Static files in development environment
if settings.DEBUG:
    urlpatterns = [
        url('media/(?P<path>.*)', django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url('', include('django.contrib.staticfiles.urls')),
    ] + urlpatterns

