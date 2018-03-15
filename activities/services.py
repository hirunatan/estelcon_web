from django.core.mail import send_mail, mail_managers
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count

from datetime import datetime, timedelta
import locale

from .models import Activity
from functools import reduce


def get_schedule():
    # Obtain the list of all activities (they are already ordered by start date) and put them in
    # a table divided in days, and then in blocks of half hour, from 8:30h to 05:00h next day.
    # Each block contains columns, and in each column fit one or more activities. Columns
    # may also span more than one block.
    # The result is a list structure like this:
    # [(day1_name, [(block1_hour, [(colspan1, rowspan1, [activ1]), (colspan2, rowspan2 [activ2, activ3])]),
    #               (block2_hour, [(colspan1, rowspan1, [activ4])])],
    #  (day2_name, [(block1_hour, [(colspan1, rowspan1, [activ5])])])]

    # Set the language for day names
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

    # Get the complete list of activities, and split into those with hour and those without
    activities = Activity.objects.all()
    activ_without_hour = [a for a in activities if a.start is None]
    activ_with_hour = [a for a in activities if a.start is not None]

    days = []
    if len(activ_with_hour) > 0:

        first_day = activ_with_hour[0].start.replace(hour=0, minute=0, second=0, microsecond=0)
        last_day = activ_with_hour[-1].start.replace(hour=0, minute=0, second=0, microsecond=0)

        # Create the list of days
        day = first_day
        while day <= last_day:

            first_block = day.replace(hour=8, minute=00)               # from 08:30h
            last_block = first_block + timedelta(hours=20, minutes=30) # until 05:00h next day
            rowspans_left = [1, 1, 1]

            # Create the list of half hour blocks
            blocks = []
            block = first_block
            while block <= last_block:

                has_data = False

                # Create the list of columns
                columns = []
                ncol = 0
                while ncol <= 2:

                    if rowspans_left[ncol] > 1:
                        rowspans_left[ncol] = rowspans_left[ncol] - 1
                        has_data = True
                    else:
                        # Create the list of activities
                        activities_column = []
                        rowspan = 1
                        for activity in activ_with_hour:
                            if (activity.start >= block) and \
                               (activity.start < (block + timedelta(minutes=30))) and \
                               activity.start.second == ncol:

                               has_data = True

                               # Calculate the block span of the activity
                               if activity.end is None:
                                   duration = 0
                               else:
                                   duration = int((activity.end - activity.start).seconds / 60)
                               activ_span = (duration - 1) / 30 + 1
                               if activ_span > rowspan:
                                   rowspan = activ_span

                               activities_column.append(activity)

                        rowspans_left[ncol] = rowspan
                        if ncol == 0:
                            colspan = 2
                            if has_data:
                                columns.append((rowspan, colspan, activities_column))
                                break
                        else:
                            colspan = 1
                            columns.append((rowspan, colspan, activities_column))

                    if ncol == 0 and has_data:
                        break
                    ncol = ncol + 1

                #if has_data:
                blocks.append((block.strftime('%H:%M'), columns))
                block = block + timedelta(minutes=30)

            # Remove all empty blocks at the beginning and the end of the day
            for i in [0, -1]:
                while len(blocks) > 0:
                    block = blocks[i]
                    has_data = False
                    for col in blocks[i][1]:
                        if len(col[2]) > 0:
                            has_data = True
                            break
                    if has_data:
                        break
                    del blocks[i]

            days.append((day.strftime('%A %d').upper(), blocks))
            day = day + timedelta(days=1)

    return (activ_without_hour, days)


def get_activity_and_status(activity_id, user):
    try:
        activity = Activity.objects.get(pk = activity_id)
    except Activity.DoesNotExist:
        return (None, {})

    is_owner = False
    is_organizer = False
    is_participant = False
    is_admin = False

    if user.is_authenticated():
        if user in activity.owners.all():
            is_owner = True
        if user in activity.organizers.all():
            is_organizer = True
        if user in activity.participants.all():
            is_participant = True
        if user.is_staff:
            is_admin = True

    user_status =  {
        'is_owner': is_owner,
        'is_organizer': is_organizer,
        'is_participant': is_participant,
        'is_admin': is_admin
    }

    return (activity, user_status)


def subscribe_to_activity(user, activity_id):
    #TODO: refactor to receive an actual activity object instead of an id
    try:
        activity = Activity.objects.get(pk = activity_id)
    except Activity.DoesNotExist:
        return

    # User is always added, even if the limit is reached
    activity.participants.add(user)
    activity.save()

    # Subscription limit control
    maxplacesreached = False
    if len(activity.participants.all()) > activity.max_places:
        maxplacesreached = True

    mail_managers(
        subject = '[Estelcon Admin] Inscripción en actividad %s' % (activity.title),
        message =
'''
El usuario %s (%s) se ha inscrito en la actividad %s.
'''
% (user.username, user.get_full_name(), activity.title),
    )

    for owner in activity.owners.all():
        send_mail(
            subject = '[Estelcon] Inscripción en actividad de la Estelcon que tú organizas',
            message =
'''
El usuario %s (%s) se ha inscrito en la actividad %s.
'''
% (user.username, user.get_full_name(), activity.title),
            from_email = settings.MAIL_FROM,
            recipient_list = [owner.email],
            fail_silently = False
        )
        if maxplacesreached:
            send_mail(
                subject = '[Estelcon] ATENCION: Tu actividad ha superado el máximo de plazas.',
                message =
'''
Ponte en contacto con la organización, por favor, ya que tu actividad '%s' ya ha sobrepasado el máximo de plazas.
Actualmente tienes %d inscritos en una actividad con un máximo establecido por ti de %d.
'''
% (activity.title, len(activity.participants.all()), activity.max_places),
                from_email = settings.MAIL_FROM,
                recipient_list = [owner.email],
                fail_silently = False
            )

    if maxplacesreached:
        message_participants_maxplaces = \
'''
ATENCION, tu inscripción ha superado el número máximo de plazas disponibles. Los responsables
ya han sido notificados de este hecho y tomarán una decisión en breve. Si no recibes
contestación en pocos días no dudes en escribir directamente a la organización.
'''
    else:
        message_participants_maxplaces = 'Te encuentras dentro del número máximo de plazas.'

    send_mail(
        subject = '[Estelcon] Inscripción en actividad de la Estelcon',
        message =
'''
Se ha registrado tu inscripción en la actividad con título '%s'.

Si en el futuro deseas cancelarla, escribe a la organización.

%s
'''
% (activity.title, message_participants_maxplaces),
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )


def change_activity(user, activity, home_url):

    mail_managers(
        subject = '[Estelcon Admin] Modificación de actividad "%s"' % (activity.title),
        message =
'''
El usuario %s (%s) ha modificado una actividad

Título: %s
Subtítulo: %s
Duración: %s
Nº máximo de plazas: %d
Mostrar responsables: %s

Texto:
%s

Necesidades logísticas:
%s

Notas para la organización:
%s'''
% (
    user.username,  user.get_full_name(), activity.title, activity.subtitle,
    activity.duration, activity.max_places or 0, activity.show_owners,
    activity.text, activity.logistics, activity.notes_organization),
)

    send_mail(
        subject = '[Estelcon] Se ha modificado la actividad "%s"' % (activity.title),
        message =
'''
Se ha modificado correctamente la actividad con título '%s'.

¡Muchas gracias por participar! Entre todos haremos una gran Mereth Aderthad.

El equipo organizador.
%s
'''
% (activity.title, home_url),
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )


def send_proposal(user, data, home_url):

    mail_managers(
        subject = '[Estelcon Admin] Actividad propuesta: %s' % (data['title']),
        message =
'''
El usuario %s (%s) ha propuesto una actividad.

Título: %s
Subtítulo: %s
Duración: %s
Nº máximo de plazas: %d
Mostrar responsables: %s
Requiere inscripción: %s

Responsables:
%s

Organizadores:
%s

Texto:
%s

Necesidades logísticas:
%s

Notas para la organización:
%s'''
% (
    user.username,  user.get_full_name(), data['title'], data['subtitle'],
    data['duration'], data['max_places'] or 0, data['show_owners'],
    data['requires_inscription'], data['owners'], data['organizers'],
    data['text'], data['logistics'], data['notes_organization']),
)

    send_mail(
        subject = '[Estelcon] Actividad propuesta para la Estelcon',
        message =
'''
Se ha enviado a los organizadores tu propuesta de actividad con título
'%s'.

Estudiaremos la actividad que propones y le buscaremos un hueco en la Estelcon. En cuanto
lo hagamos, podrás ver cómo aparece en el Programa de actividades, incluyendo una ficha
rellena con los datos que nos has enviado (al menos con la parte pública). Y si tú o
cualquiera de las personas designadas como responsables accedéis a la web con vuestro
usuario y contraseña, podréis consultar y modificar todos los datos.

Si tenemos alguna duda o consulta que hacerte, contactaremos contigo a través del correo
electrónico o el teléfono que indicaste al registrarte.

¡Muchas gracias por participar! Entre todos haremos una gran Mereth Aderthad.

El equipo organizador.
%s
'''
% (data['title'], home_url),
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )

