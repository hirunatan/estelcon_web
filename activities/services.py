from django.core.mail import send_mail, mail_managers
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count

from datetime import datetime, timedelta
from collections import namedtuple
import locale
import math

from .models import Activity
from functools import reduce


Day = namedtuple('Day', ['name', 'blocks'])
Block = namedtuple('Block', ['hour', 'columns'])
Column = namedtuple('Column', ['rowspan', 'colspan', 'activities'])
PendingColumn = namedtuple('PendingColumn', ['current_row', 'column'])

def get_schedule():
    # Obtain the list of all activities (they are already ordered by start date) and put them in
    # a table divided in days, and then in blocks of half hour, from 8:30h to 05:00h next day.
    # Each block contains columns, and in each column fit one or more activities. Columns
    # may also span more than one block.

    # Set the language for day names
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

    # Get the complete list of activities, and split into those with hour and those without
    activities = Activity.objects.all()
    activ_without_hour = [a for a in activities if a.start is None]
    activ_with_hour = [a for a in activities if a.start is not None]

    # Create the list of days
    days = []
    if len(activ_with_hour) > 0:

        first_day = activ_with_hour[0].start.replace(hour=0, minute=0, second=0, microsecond=0)
        last_day = activ_with_hour[-1].start.replace(hour=0, minute=0, second=0, microsecond=0)

        day = first_day
        while day <= last_day:
            day_blocks = _build_day_blocks(activ_with_hour, day)
            days.append(day_blocks)
            day = day + timedelta(days=1)

    return (activ_without_hour, days)


def _build_day_blocks(activ_with_hour, day):
    first_block_hour = day.replace(hour=8, minute=00)                     # from 08:30h
    last_block_hour = first_block_hour + timedelta(hours=20, minutes=30)  # until 05:00h next day

    pending_cols = [
        PendingColumn(0, Column(1, 2, [])),
        PendingColumn(0, Column(1, 1, [])),
        PendingColumn(0, Column(1, 1, []))
    ]

    # Create a list of 30min blocks
    blocks = []
    block_hour = first_block_hour
    while block_hour <= last_block_hour:

        block = _build_block(activ_with_hour, block_hour, pending_cols)
        if block:
            blocks.append(block)

        block_hour = block_hour + timedelta(minutes=30)

    # Remove all empty blocks at the beginning and the end of the day
    for i in [0, -1]:
        while len(blocks) > 0:
            block = blocks[i]
            if not block.columns:
                del blocks[i]
            else:
                break

    return Day(day.strftime('%A %d').upper(), blocks)


def _build_block(activ_with_hour, block_hour, pending_cols):

    for ncol in range(3):
        rowspan, activities = _get_block_activities(activ_with_hour, block_hour, ncol)

        current_row, column = pending_cols[ncol]

        column.activities.extend(activities)
        if rowspan > column.rowspan - current_row:
            column = Column(rowspan + current_row, column.colspan, column.activities)

        pending_cols[ncol] = PendingColumn(current_row, column)

    if pending_cols[0].column.activities:
        if pending_cols[0].current_row == 0:
            columns = [pending_cols[0].column]
        else:
            columns = []
        if pending_cols[1].column.activities:
            columns[0].activities.extend(pending_cols[1].column.activities)
        if pending_cols[2].column.activities:
            columns[0].activities.extend(pending_cols[2].column.activities)
    else:
        columns = []
        if pending_cols[1].current_row == 0 and pending_cols[1].column.activities:
            columns.append(pending_cols[1].column)
        if pending_cols[2].current_row == 0 and pending_cols[2].column.activities:
            columns.append(pending_cols[2].column)

    for ncol in range(3):
        current_row, column = pending_cols[ncol]

        current_row += 1
        if current_row >= column.rowspan:
            current_row = 0
            column = Column(1, column.colspan, [])

        pending_cols[ncol] = PendingColumn(current_row, column)

    return Block(block_hour.strftime('%H:%M'), columns)


def _get_block_activities(activ_with_hour, block_hour, ncol):
    activities = []
    rowspan = 1
    for activity in activ_with_hour:
        if (activity.start >= block_hour) and \
           (activity.start < (block_hour + timedelta(minutes=30))) and \
           (activity.start.second == ncol):

            activities.append(activity)

            if activity.end is None:
                duration = 0
            else:
                duration = math.ceil((activity.end - activity.start).seconds / 60)
 
            activ_span = math.ceil(duration / 30)
            if activ_span > rowspan:
                rowspan = activ_span

    return (rowspan, activities)


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

