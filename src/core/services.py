# -*- coding: utf-8 -*-

from django.core.mail import send_mail, mail_managers
from django.conf import settings

from .models import UserProfile, Activity


def get_activities_owned_by(user):
    return Activity.objects.filter(owners = user)

def get_activities_organized_by(user):
    return Activity.objects.filter(organizers = user)

def get_activities_in_which_participates(user):
    return Activity.objects.filter(participants = user)

def get_activities_to_participate_by(user):
    return Activity.objects.filter(requires_inscription = True).exclude(participants = user)

def change_user_personal_data(user, new_data):
    user.username = new_data['username'];
    user.email = new_data['email'];
    if new_data['password1']:
        user.set_password(new_data['password1']);
    user.first_name=new_data['first_name']
    user.last_name=new_data['last_name']
    user.save()

    profile = user.profile
    profile.alias=new_data['alias']
    profile.smial=new_data['smial']
    profile.phone=new_data['phone']
    profile.city=new_data['city']
    profile.age=new_data['age']
    profile.save()

    mail_managers(
        subject = u'[Estelcon Admin] Modificación de datos personales de usuario %s' % (user.get_full_name()),
        message =
u'''
%s, con usuario %s y email %s, ha modificado sus datos personales en la web.
Su ficha puede consultarse directamente en %s
'''
% (user.get_full_name(), user.username, user.email, profile.get_admin_url()),
    )

    send_mail(
        subject = u'[Estelcon] Notificación de modificación de ficha personal',
        message =
u'''
Datos modificados.

Se ha registrado correctamente el cambio de tus datos personales. Puedes consultarlos entrando en
tu ficha personal. Un saludo.

El equipo organizador.
%s
'''
% (settings.PROTOCOL + '://' + settings.SITE_URL),
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )


def change_user_inscription_data(user, new_data):
    profile = user.profile
    profile.notes_food=new_data['notes_food']
    profile.notes_transport=new_data['notes_transport']
    profile.notes_general=new_data['notes_general']
    profile.dinner_menu=new_data['dinner_menu']
    profile.shirts_S=new_data['shirts_S']
    profile.shirts_M=new_data['shirts_M']
    profile.shirts_L=new_data['shirts_L']
    profile.shirts_XL=new_data['shirts_XL']
    profile.shirts_XXL=new_data['shirts_XXL']
    profile.save()

    mail_managers(
        subject = u'[Estelcon Admin] Modificación de datos de inscripción de usuario %s' % (user.get_full_name()),
        message =
u'''
%s, con usuario %s y email %s, ha modificado sus datos de inscripción en la web.
Su ficha puede consultarse directamente en %s
'''
% (user.get_full_name(), user.username, user.email, profile.get_admin_url()),
    )

    send_mail(
        subject = u'[Estelcon] Notificación de modificación de ficha personal',
        message =
u'''
Datos modificados.

Se ha registrado correctamente el cambio de tus datos de inscripción. Puedes consultarlos entrando en
tu ficha personal. Un saludo.

El equipo organizador.
%s
'''
% (settings.PROTOCOL + '://' + settings.SITE_URL),
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )

