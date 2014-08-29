# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import models as auth_models

from . import models

class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = u'perfil'

class UserAdmin(auth_admin.UserAdmin):
    inlines = (UserProfileInline, )

class ActivityAdmin(admin.ModelAdmin):
    pass

admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdmin)
admin.site.register(models.Activity, ActivityAdmin)

