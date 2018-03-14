# -*- encoding: utf-8 -*-

import django

from django.conf.urls import include, url
from django.conf.urls.static import static
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
    urlpatterns = urlpatterns + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

