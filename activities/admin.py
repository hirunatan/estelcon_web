from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import models as auth_models
from django.utils.translation import ugettext, ugettext_lazy as _

from . import models


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'duration', 'column', 'has_view_page', 'show_owners', 'requires_inscription')
    list_filter = ('has_view_page', 'show_owners', 'requires_inscription')
    search_fields = ('title', 'subtitle', 'text', 'logistics', 'notes_organization')
    filter_horizontal = ('owners', 'organizers', 'participants')

admin.site.register(models.Activity, ActivityAdmin)

