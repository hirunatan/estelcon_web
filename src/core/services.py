# -*- coding: utf-8 -*-

from django.core.mail import send_mail, mail_managers
from django.conf import settings

from datetime import datetime, timedelta

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
		blocks.append((block.strftime("%H:%M"), columns))
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

	    days.append((day.strftime("%A %d").decode("iso-8859-15").upper(), blocks))
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

