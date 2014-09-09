# -*- coding: utf-8 -*-

from django.core.mail import send_mail, mail_managers
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from datetime import datetime, timedelta

from .models import UserProfile, Activity

MAX_USERS = 186

def create_new_user(user_data, home_url):

    quota = 0
    if user_data['day_1']:
    	quota += 35
    if user_data['day_2']:
    	quota += 35
    if user_data['day_3']:
    	quota += 70

    queue = max(0, UserProfile.objects.count() - MAX_USERS)

    user = User.objects.create_user(username=user_data['username'],
                                    email=user_data['email'],
                                    password=user_data['password1'])
    user.first_name=user_data['first_name']
    user.last_name=user_data['last_name']
    user.is_staff = False
    user.is_active = True
    user.is_superuser = False
    user.save()

    profile = UserProfile.objects.create(
        user = user,
        alias = user_data['alias'],
        smial = user_data['smial'],
        phone = user_data['phone'],
        city = user_data['city'],
        age = user_data['age'],
        payment = '',
        notes_food = user_data['notes_food'],
        notes_transport = user_data['notes_transport'],
        notes_general = user_data['notes_general'],
        dinner_menu = user_data['dinner_menu'],
        shirts_S = user_data['shirts_S'],
        shirts_M = user_data['shirts_M'],
        shirts_L = user_data['shirts_L'],
        shirts_XL = user_data['shirts_XL'],
        shirts_XXL = user_data['shirts_XXL'],
        day_1 = user_data['day_1'],
        day_2 = user_data['day_2'],
        day_3 = user_data['day_3'],
        quota = quota,
        payed = 0,
    )

    if not queue:
        profile.payment = \
u'''
Pendiente de verificación del pago. Debes realizar un ingreso de %d€ en la cuenta de La Caixa
2100 1923 91 01 00148021 a nombre de PABLO RUIZ MUZQUIZ, indicando en el ingreso el código %s.
''' % (profile.quota, profile.get_payment_code())
    else:
	profile.payment = \
u'''
En cola de espera con posición %d. La cuota es de %d€ y el código %s, pero no debes hacer
ningún ingreso hasta que se pueda confirmar tu asistencia.
''' % (queue, profile.quota, profile.get_payment_code())
    profile.save()

    mail_managers(
        subject = u'[Estelcon Admin] Nueva inscripción en la Estelcon: %s (%s)' % (user.username, user.get_full_name()),
        message =
u'''
Se ha creado una nueva ficha para %s, con usuario %s y email %s.
Su ficha puede consultarse directamente en %s
'''
% (user.get_full_name(), user.username, user.email, profile.get_admin_url()),
    )

    if not queue:
	message_user = \
u'''
¡Gracias por inscribirte en la XIV Mereth Aderthad, %s!.

Ya hemos registrado tus datos, y se ha creado un usuario para que puedas acceder a la web, ver y
cambiar tus datos personales, y apuntarte a actividades o proponernos las tuyas propias.

La inscripción queda pendiente de verificación del pago. Debes realizar un ingreso de %d€ en
la cuenta de La Caixa 2100 1923 91 01 00148021 a nombre de PABLO RUIZ MUZQUIZ, indicando en el ingreso el código %s.

Esperamos que esta Mereth Aderthad sea una experiencia inolvidable.

El equipo organizador.
%s
''' % (user.first_name, profile.quota, profile.get_payment_code(), home_url)
    else:
	message_user = \
u'''
¡Gracias por inscribirte en la XIV Mereth Aderthad, %s!.

Sin embargo, lamentamos comunicarte que el número de plazas máximo que teníamos establecido ha sido alcanzado, por
lo que no podemos garantizar tu asistencia. ¡Lo sentimos muchísimo!

Pero de todas formas, te ponemos en cola de espera por si aparece un hueco vacante y podemos dar paso a tu inscripción.
Tu posición en la cola es la %d. Hemos registrado tus datos y se ha creado un usuario con el que puedes acceder a la
web y consultar el estado de tu petición. La cuota que te corresponde es de %d€ y el código de pago es %s, pero no
hagas ningún ingreso todavía hasta que se pueda confirmar tu asistencia.

Esperamos que tengas suerte y puedas disfrutar de esta Mereth Aderthad.

El equipo organizador.
%s
''' % (user.first_name, queue, profile.quota, profile.get_payment_code(), home_url)

    send_mail(
        subject = u'[Estelcon] Notificación de inscripción en la Estelcon',
        message = message_user,
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )

    return (user, queue)


def retrieve_user(username):
    try:
        return User.objects.get(username = username)
    except User.DoesNotExist:
        return None


def authenticate_user(username, password):
    return authenticate(username = username, password = password)


def send_password_reminder(user, change_password_url_pattern):
    profile = user.profile
    profile.generate_reminder_code()
    profile.save()

    send_mail(
        subject = u'[Estelcon] Olvido de contraseña',
        message =
u'''
Para cambiar tu contraseña visita el siguiente enlace:

%s
'''
% (change_password_url_pattern % profile.lost),
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )


def validate_reminder_code(reminder_code):
    try:
        profile = UserProfile.objects.get(lost = reminder_code)
        return profile.user
    except UserProfile.DoesNotExist:
        return None


def change_user_password(user, password):
    user.set_password(password)
    user.save()

    profile = user.profile
    profile.reset_reminder_code()
    profile.save()


def get_activities_owned_by(user):
    return Activity.objects.filter(owners = user)


def get_activities_organized_by(user):
    return Activity.objects.filter(organizers = user)


def get_activities_in_which_participates(user):
    return Activity.objects.filter(participants = user)


def get_activities_to_participate_by(user):
    return Activity.objects.filter(requires_inscription = True).exclude(participants = user)


def change_user_personal_data(user, new_data, home_url):
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
% home_url,
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )


def change_user_inscription_data(user, new_data, home_url):
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
% home_url,
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )


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
    #locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

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

	    first_block = day.replace(hour=8, minute=30)               # from 08:30h
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

	    days.append((day.strftime('%A %d').decode('iso-8859-15').upper(), blocks))
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
        subject = u'[Estelcon Admin] Inscripción en actividad %s' % (activity.title),
        message =
u'''
El usuario %s (%s) se ha inscrito en la actividad %s.
'''
% (user.username, user.get_full_name(), activity.title),
    )

    for owner in activity.owners.all():
	send_mail(
            subject = u'[Estelcon] Inscripción en actividad de la Estelcon que tú organizas',
            message =
u'''
El usuario %s (%s) se ha inscrito en la actividad %s.
'''
% (user.username, user.get_full_name(), activity.title),
            from_email = settings.MAIL_FROM,
            recipient_list = [owner.email],
            fail_silently = False
        )
        if maxplacesreached:
	    send_mail(
                subject = u'[Estelcon] ATENCION: Tu actividad ha superado el máximo de plazas.',
                message =
u'''
Ponte en contacto con la organización, por favor, ya que tu actividad '%s' ya ha sobrepasado el máximo de plazas.
Actualmente tienes %d inscritos en una actividad con un máximo establecido por ti de %d.
'''
% (activity.title, len(activity.participants.all()), activity.max_places),
                from_email = settings.MAIL_FROM,
                recipient_list = [owner.email],
                fail_silently = False
            )

    if maxplacesreached:
        message_participants_maxplaces = u'ATENCION, tu inscripción ha superado el número máximo de plazas disponibles. Los responsables ya han sido notificados de este hecho y tomarán una decisión en breve. Si no recibes contestación en pocos días no dudes en escribir directamente a info@estelcon2008.org.'
    else:
        message_participants_maxplaces = u'Te encuentras dentro del número máximo de plazas.'

    send_mail(
        subject = u'[Estelcon] Inscripción en actividad de la Estelcon',
        message =
u'''
Se ha registrado tu inscripción en la actividad con título '%s'.

Si en el futuro deseas cancelarla, escribe directamente a info@estelcon2008.org.

%s
'''
% (activity.title, message_participants_maxplaces),
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )


def send_proposal(user, data, home_url):

    mail_managers(
        subject = u'[Estelcon Admin] Actividad propuesta: %s' % (data['title']),
        message =
u'''
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
        subject = u'[Estelcon] Actividad propuesta para la Estelcon',
        message =
u'''
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

