from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import models as auth_models
from django.utils.translation import ugettext, ugettext_lazy as _

from . import models


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    exclude = ('lost',)
    verbose_name_plural = 'perfil'


class UserAdmin(auth_admin.UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'is_staff', 'get_payment_code', 'get_is_under_age', 'get_quota', 'get_payed', 'get_payment')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__dinner_menu', 'profile__room_choice', 'profile__want_mentor', 'profile__want_media')
    select_related = ('profile',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__alias', 'profile__smial', 'profile__payment')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = (UserProfileInline, )

    def get_payment_code(self, obj):
        return obj.profile.payment_code

    get_payment_code.short_description = 'C. pago'

    def get_is_under_age(self, obj):
        return obj.profile.is_under_age

    get_is_under_age.short_description = 'Menor de edad'

    def get_quota(self, obj):
        return obj.profile.quota

    get_quota.short_description = 'Cuota'

    def get_payed(self, obj):
        return obj.profile.payed

    get_payed.short_description = 'Pagado'

    def get_payment(self, obj):
        return obj.profile.payment[:40]

    get_payment.short_description = 'Estado de pago'

admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdmin)

