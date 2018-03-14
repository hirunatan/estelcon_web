from django.core.mail import send_mail, mail_managers
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count

from datetime import datetime, timedelta
import locale

from .models import UserProfile
from functools import reduce

MAX_USERS = 150

#TODO: usar templates para los textos de los correos

def pre_register_user(user_data, home_url):

    mail_managers(
        subject = '[Estelcon Admin] Nueva preinscripción en la Estelcon: %s %s' % (
            user_data['first_name'], user_data['last_name']
        ),
        message =
'''
Se ha preinscrito un nuevo usuario con nombre %s %s.

 - Alias: %s
 - Smial: %s
 - Email: %s
 - Teléfono: %s
 - Población: %s
 - Edad: %s
 - Viernes / sábado: %s
 - Sábado / domingo: %s
 - Domingo / lunes + cena de gala: %s

Notas:
%s
'''
% (user_data['first_name'], user_data['last_name'], user_data['alias'], user_data['smial'],
   user_data['email'], user_data['phone'], user_data['city'], user_data['age'],
   'Sí' if user_data['day_1'] else 'No',
   'Sí' if user_data['day_2'] else 'No',
   'Sí' if user_data['day_3'] else 'No',
   user_data['notes']),
    )


def create_new_user(user_data, home_url):

    quota = _calculate_quota(user_data)

    if user_data['room_choice'] not in ["sin-alojamiento", "otros"]:
        queue = max(0, UserProfile.objects.filter(room_choice__in=["sin-alojamiento", "otros"]).count() - MAX_USERS)
    else:
        queue = 0

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
        notes_food = user_data['notes_food'],
        dinner_menu = user_data['dinner_menu'],
        day_1 = user_data['day_1'],
        day_2 = user_data['day_2'],
        day_3 = user_data['day_3'],
        notes_transport = user_data['notes_transport'],
        room_choice = user_data['room_choice'],
        room_preferences = user_data['room_preferences'],
        children_count = user_data['children_count'],
        children_names = user_data['children_names'],
        is_ste_member = user_data['is_ste_member'],
        want_ste_member = user_data['want_ste_member'],
        squire = user_data['squire'],
        first_estelcon = user_data['first_estelcon'],
        want_boat = user_data['want_boat'],
        notes_general = user_data['notes_general'],
        shirts_S = user_data['shirts_S'],
        shirts_M = user_data['shirts_M'],
        shirts_L = user_data['shirts_L'],
        shirts_XL = user_data['shirts_XL'],
        shirts_XXL = user_data['shirts_XXL'],
        quota = quota,
        payed = 0,
        payment = '',
    )

    if not queue:
        if quota > 0:
#            profile.payment = \
#u'''
#Pendiente de pago. Los pagos no están habilitados todavía, estamos terminando de cerrar las
#condiciones. Recuerda tu importe de %d€ y tu código de inscripción %s, en breve te
#enviaremos más instrucciones.
#''' % (profile.quota, profile.payment_code)
            profile.payment = \
'''
Pendiente de verificación del pago. Debes realizar un ingreso de %d€ en la cuenta de Caixabank
ES15 2100 0435 5702 0039 4933 a nombre de Juan Carlos Sauri, indicando en el ingreso el código %s.

Por favor recuerda hacer el ingreso antes de 5 días. Si no se recibe el pago con
anterioridad a esa fecha, tu plaza quedará anulada.
''' % (profile.quota, profile.payment_code)
        else:
            profile.payment = \
'''
Ponte en contacto con la organización para que te indiquemos el importe a pagar y la forma de pago.
'''
    else:
        profile.payment = \
'''
En cola de espera con posición %d. La cuota es de %d€ y el código %s, pero no debes hacer
ningún ingreso hasta que se pueda confirmar tu asistencia.
''' % (queue, profile.quota, profile.payment_code)
    profile.save()

    mail_managers(
        subject = '[Estelcon Admin] Nueva inscripción en la Estelcon: %s (%s)' % (user.username, user.get_full_name()),
        message =
'''
Se ha creado una nueva ficha para %s, con usuario %s y email %s.
Su ficha puede consultarse directamente en %s
'''
% (user.get_full_name(), user.username, user.email, profile.get_admin_url()),
    )

    if not queue:
        if profile.quota > 0:
#            message_user = \
#u'''
#¡Gracias por inscribirte en la Mereth Aderthad, %s!.
#
#Ya hemos registrado tus datos, y se ha creado un usuario para que puedas acceder a la web, ver y
#cambiar tus datos personales, y apuntarte a actividades o proponernos las tuyas propias.
#
#El siguiente paso sería realizar el pago, pero los pagos no están habilitados todavía, estamos
#terminando de cerrar las condiciones. En breve te enviaremos más instrucciones, recuerda tu
#importe de %s€ y tu código de inscripción %s.
#
#Esperamos que esta Mereth Aderthad sea una experiencia inolvidable.
#
#El equipo organizador.
#%s
#''' % (user.first_name, profile.quota, profile.payment_code, home_url)
            message_user = \
'''
¡Gracias por inscribirte en la Mereth Aderthad, %s!.

Ya hemos registrado tus datos, y se ha creado un usuario para que puedas acceder a la web, ver y
cambiar tus datos personales, y apuntarte a actividades o proponernos las tuyas propias.

La inscripción queda pendiente de verificación del pago. Debes realizar un ingreso de %d€ en la
cuenta de Caixabank ES15 2100 0435 5702 0039 4933 a nombre de Juan Carlos Sauri, indicando en el
ingreso el código %s.

Por favor recuerda hacer el ingreso antes de 5 días. Si no se recibe el pago con
anterioridad a esa fecha, tu plaza quedará anulada.

Esperamos que esta Mereth Aderthad sea una experiencia inolvidable.

El equipo organizador.
%s
''' % (user.first_name, profile.quota, profile.payment_code, home_url)
        else:
            message_user = \
'''
¡Gracias por inscribirte en la Mereth Aderthad, %s!.

Ya hemos registrado tus datos, y se ha creado un usuario para que puedas acceder a la web, ver y
cambiar tus datos personales, y apuntarte a actividades o proponernos las tuyas propias.

La inscripción queda pendiente de pago, pero tu opción de inscripción requiere que contactes
con la organización para que te indiquemos el importe a abonar y la forma de pago.

Esperamos que esta Mereth Aderthad sea una experiencia inolvidable.

El equipo organizador.
%s
''' % (user.first_name, home_url)

    else:
        message_user = \
'''
¡Gracias por inscribirte en la Mereth Aderthad, %s!.

Sin embargo, lamentamos comunicarte que el número de plazas máximo que tenemos ha sido alcanzado, por
lo que no podemos garantizar tu alojamiento. ¡Lo sentimos muchísimo!

Pero de todas formas, te ponemos en cola de espera por si aparece un hueco vacante y podemos dar paso a tu inscripción.
Tu posición en la cola es la %d. Hemos registrado tus datos y se ha creado un usuario con el que puedes acceder a la
web y consultar el estado de tu petición. La cuota que te corresponde es de %d€ y el código de pago es %s, pero no
hagas ningún ingreso todavía hasta que se pueda confirmar tu asistencia.

Esperamos que tengas suerte y puedas disfrutar de esta Mereth Aderthad.

El equipo organizador.
%s
''' % (user.first_name, queue, profile.quota, profile.payment_code, home_url)

    send_mail(
        subject = '[Estelcon] Notificación de inscripción en la Estelcon',
        message = message_user,
        from_email = settings.MAIL_FROM,
        recipient_list = [user.email],
        fail_silently = True
    )

    return (user, queue)


def _calculate_quota(user_data):
    if user_data['room_choice'] == 'albergue-completa':
        quota = 175.0
    elif user_data['room_choice'] == 'albergue-v-a-d':
        quota = 150.0
    elif user_data['room_choice'] == 'albergue-s-y-d':
        quota = 125.0
    elif user_data['room_choice'] == 'doble-completa':
        quota = 195.0
    elif user_data['room_choice'] == 'doble-v-a-d':
        quota = 175.0
    elif user_data['room_choice'] == 'doble-s-y-d':
        quota = 140.0
    elif user_data['room_choice'] == 'sin-alojamiento':
        quota = 120.0
    else:
        return 0.0

    if user_data['age'] <= 12:
        quota = quota * 0.75

    if not user_data['is_ste_member'] and user_data['room_choice'] != 'sin-alojamiento':
        quota += 10.0

    if user_data['want_ste_member']:
        if user_data['room_choice'] != 'sin-alojamiento':
            quota += 2.0
        else:
            quota += 12.0

    if user_data['want_boat']:
        quota += 15.0

    num_shirts = user_data['shirts_S'] + \
                 user_data['shirts_M'] + \
                 user_data['shirts_L'] + \
                 user_data['shirts_XL'] + \
                 user_data['shirts_XXL']
    quota += num_shirts * 12.0

    #if user_data['room_choice'] == 'sin-alojamiento':

    #    if user_data['dinner_menu'] == 'sin-cena':
    #        quota += 12
    #    else:
    #        quota += 36

    #else:

    #    if user_data['room_choice'].startswith('triple') or user_data['room_choice'] == 'otros':
    #        quota += 11.2
    #        if user_data['day_1']:
    #            quota += 39.6
    #        if user_data['day_2']:
    #            quota += 39.6
    #        if user_data['day_3']:
    #            quota += 54.6

    #    if user_data['room_choice'].startswith('doble'):
    #        quota += 11.2
    #        if user_data['day_1']:
    #            quota += 46.6
    #        if user_data['day_2']:
    #            quota += 46.6
    #        if user_data['day_3']:
    #            quota += 61.6

    #    if user_data['age'] <= 12:
    #        quota = quota * 0.75

    #    if not user_data['is_ste_member'] and user_data['age'] > 12:
    #        quota += 10.0

    #    if user_data['want_ste_member'] and user_data['age'] > 12:
    #        quota += 2.0

    #num_shirts = user_data['shirts_S'] + \
    #             user_data['shirts_M'] + \
    #             user_data['shirts_L'] + \
    #             user_data['shirts_XL'] + \
    #             user_data['shirts_XXL']
    #quota += num_shirts * 10.0

    return round(quota)


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
        subject = '[Estelcon] Olvido de contraseña',
        message =
'''
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
    return []
    # return Activity.objects.filter(owners = user)


def get_activities_organized_by(user):
    return []
    # return Activity.objects.filter(organizers = user)


def get_activities_in_which_participates(user):
    return []
    # return Activity.objects.filter(participants = user)


def get_activities_to_participate_by(user):
    return []
    # return Activity.objects.filter(requires_inscription = True).exclude(participants = user)


def change_user_personal_data(user, new_data, home_url):
    changed_fields = []

    if new_data['password1']:
        user.set_password(new_data['password1']);

    for field_name in ['username', 'email', 'first_name', 'last_name']:
        if getattr(user, field_name) != new_data[field_name]:
            changed_fields.append(str(user._meta.get_field_by_name(field_name)[0].verbose_name))
            setattr(user, field_name, new_data[field_name])
    user.save()

    profile = user.profile
    for field_name in ['alias', 'smial', 'phone', 'city', 'age']:
        if getattr(profile, field_name) != new_data[field_name]:
            changed_fields.append(str(profile._meta.get_field_by_name(field_name)[0].verbose_name))
            setattr(profile, field_name, new_data[field_name])
    profile.save()

    changed_text = '\n'.join(['* %s' % (field) for field in changed_fields])
    mail_managers(
        subject = '[Estelcon Admin] Modificación de datos personales de usuario %s' % (user.get_full_name()),
        message =
'''
%s, con usuario %s y email %s, ha modificado sus datos personales en la web:

%s

Su ficha puede consultarse directamente en %s
'''
% (user.get_full_name(), user.username, user.email, changed_text, profile.get_admin_url()),
    )

    send_mail(
        subject = '[Estelcon] Notificación de modificación de ficha personal',
        message =
'''
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
    changed_fields = []

    profile = user.profile
    for field_name in ['notes_food', 'dinner_menu', 'notes_transport', 'room_choice',
                'room_preferences', 'squire', 'notes_general', 'shirts_S', 'shirts_M',
                'shirts_L', 'shirts_XL', 'shirts_XXL',
            ]:
        if getattr(profile, field_name) != new_data[field_name]:
            changed_fields.append(str(profile._meta.get_field_by_name(field_name)[0].verbose_name))
            setattr(profile, field_name, new_data[field_name])
    profile.save()

    changed_text = '\n'.join(['* %s' % (field) for field in changed_fields])
    mail_managers(
        subject = '[Estelcon Admin] Modificación de datos de inscripción de usuario %s' % (user.get_full_name()),
        message =
'''
%s, con usuario %s y email %s, ha modificado sus datos de inscripción en la web:

%s

Su ficha puede consultarse directamente en %s
'''
% (user.get_full_name(), user.username, user.email, changed_text, profile.get_admin_url()),
    )

    send_mail(
        subject = '[Estelcon] Notificación de modificación de ficha personal',
        message =
'''
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


def user_listing(listing_id):
    if listing_id == 1:
        return listing_all_users_accommodation()
    elif listing_id == 2:
        return listing_all_users_travel()
    elif listing_id == 3:
        return listing_non_members()
    elif listing_id == 4:
        return listing_squires()
    elif listing_id == 5:
        return listing_children()
    elif listing_id == 6:
        return listing_dinner_menus()
    elif listing_id == 7:
        return listing_unpaid_users()
    elif listing_id == 8:
        return listing_paid_users()
    elif listing_id == 9:
        return listing_reserved_shirts()
    elif listing_id == 10:
        return listing_users_with_shirts()
    elif listing_id == 11:
        return listing_umbarians()
    elif listing_id == 12:
        return listing_everything()
    else:
        return None


def listing_all_users_accommodation():
    profiles = UserProfile.objects.order_by('user__first_name', 'user__last_name')

    rows = [(
        p.user.get_full_name(),
        p.alias,
        p.smial,
        'x' if p.day_1 else '',
        'x' if p.day_2 else '',
        'x' if p.day_3 else '',
        p.room_choice,
        p.room_preferences,
        p.notes_food,
    ) for p in profiles]

    rows = [("Nombre", "Pseudónimo", "Smial", "Viernes", "Sábado", "Domingo", "Habitación", "Dormir", "Comida")] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)


def listing_all_users_travel():
    profiles = UserProfile.objects.order_by('user__first_name', 'user__last_name')

    rows = [(
        p.user.get_full_name(),
        p.alias,
        p.smial,
        p.city,
        p.notes_transport,
    ) for p in profiles]

    rows = [("Nombre", "Pseudónimo", "Smial", "Procedencia", "Viaje")] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)


def listing_non_members():
    profiles = UserProfile.objects.filter(is_ste_member = False).order_by('user__first_name', 'user__last_name')

    rows = [(
        p.user.get_full_name(),
        'x' if p.want_ste_member else '',
    ) for p in profiles]

    rows = [("Nombre", "Quiere ser socio")] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)


def listing_squires():
    profiles = UserProfile.objects.filter(squire = True).order_by('user__first_name', 'user__last_name')

    rows = [(
        p.user.get_full_name(),
    ) for p in profiles]

    rows = [("Nombre",)] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)


def listing_children():
    profiles = UserProfile.objects.filter(age__lt = 15).order_by('user__first_name', 'user__last_name')

    rows = [(
        p.user.get_full_name(),
        p.alias,
        p.smial,
        p.age,
    ) for p in profiles]

    rows = [("Nombre", "Pseudónimo", "Smial", "Edad")] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)


def listing_dinner_menus():
    menus = UserProfile.objects.all().values('dinner_menu').annotate(requests=Count('dinner_menu')).order_by()

    rows = [(
        m['dinner_menu'],
        m['requests'],
    ) for m in menus]

    rows = [("Menú", "Peticiones")] + rows
    block = ""
    return (block, rows)


def listing_unpaid_users():
    profiles = UserProfile.objects.filter(payment__contains='Pendiente de verificación del pago')

    rows = [(p.user.get_full_name(), p.user.email, p.quota, p.payed) for p in profiles]
    rows.sort(key=lambda p: p[0].lower())

    rows = [("Nombre", "Email", "Por pagar", "Pagado")] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)


def listing_paid_users():
    profiles = UserProfile.objects.exclude(payment__contains='Pendiente de verificación del pago')

    rows = [(p.user.get_full_name(), p.user.email, p.quota, p.payed) for p in profiles]
    rows.sort(key=lambda p: p[0].lower())

    rows = [("Nombre", "Email", "Por pagar", "Pagado")] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)


def listing_reserved_shirts():
    profiles = UserProfile.objects.all()

    sums = reduce(lambda sums, row: (sums[0]+row.shirts_S,
                                     sums[1]+row.shirts_M,
                                     sums[2]+row.shirts_L,
                                     sums[3]+row.shirts_XL,
                                     sums[4]+row.shirts_XXL),
                  profiles,
                  (0, 0, 0, 0, 0))

    rows = [("TallaS", "TallaM", "TallaL", "TallaXL", "TallaXXL"), sums]
    return (None, rows)


def listing_users_with_shirts():
    profiles = UserProfile.objects.all()

    rows = []

    rows1 = [("talla S", p.user.get_full_name(), p.shirts_S) for p in profiles if p.shirts_S > 0]
    rows1.sort(key=lambda p: p[1].lower())
    rows += rows1

    rows1 = [("talla M", p.user.get_full_name(), p.shirts_M) for p in profiles if p.shirts_M > 0]
    rows1.sort(key=lambda p: p[1].lower())
    rows += rows1

    rows1 = [("talla L", p.user.get_full_name(), p.shirts_L) for p in profiles if p.shirts_L > 0]
    rows1.sort(key=lambda p: p[1].lower())
    rows += rows1

    rows1 = [("talla XL", p.user.get_full_name(), p.shirts_XL) for p in profiles if p.shirts_XL > 0]
    rows1.sort(key=lambda p: p[1].lower())
    rows += rows1

    rows1 = [("talla XXL", p.user.get_full_name(), p.shirts_XXL) for p in profiles if p.shirts_XXL > 0]
    rows1.sort(key=lambda p: p[1].lower())
    rows += rows1

    rows = [("Talla", "Nombre", "Cantidad")] + rows
    return (None, rows)

def listing_umbarians():
    profiles = UserProfile.objects.filter(want_boat=True).order_by('user__first_name', 'user__last_name')

    rows = [(
        p.user.get_full_name(),
        p.alias,
        p.smial,
    ) for p in profiles]

    rows = [("Nombre", "Pseudónimo", "Smial")] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)


def listing_everything():
    profiles = UserProfile.objects.order_by('user__first_name', 'user__last_name')

    rows = [(
        p.user.get_full_name(),
        p.user.email,
        'x' if p.user.is_staff else '',
        p.alias,
        p.smial,
        p.phone,
        p.city,
        p.age,
        p.dinner_menu,
        p.notes_food,
        'x' if p.day_1 else '',
        'x' if p.day_2 else '',
        'x' if p.day_3 else '',
        p.notes_transport,
        p.room_choice,
        p.room_preferences,
        p.children_count,
        p.children_names,
        'x' if p.is_ste_member else '',
        'x' if p.want_ste_member else '',
        'x' if p.squire else '',
        'x' if p.first_estelcon else '',
        'x' if p.want_boat else '',
        p.notes_general,
        p.shirts_S,
        p.shirts_M,
        p.shirts_L,
        p.shirts_XL,
        p.shirts_XXL,
        p.payment_code,
        p.quota,
        p.payed,
        p.payment,
    ) for p in profiles]

    rows = [("Nombre", "Email", "Staff", "Pseudónimo", "Smial", "Teléfono", "Población", "Edad", "Menú",
             "Comida", "Viernes", "Sábado", "Domingo", "Transporte", "Habitación", "Dormir", "Nº hijos",
             "Hijos", "Es socio", "Quiere ser", "Escudero", "Primera vez", "Barco", "Notas", "S", "M",
             "L", "XL", "XXL", "Código", "Cuota", "Pagado", "Estado de pago")] + rows
    block = ", ".join(['"' + p.user.get_full_name() + '" <' + p.user.email + '>' for p in profiles])
    return (block, rows)

