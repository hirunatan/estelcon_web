# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from random import choice
import string


class UserProfile(models.Model):
    # Link with the Django user
    user = models.OneToOneField(User, related_name='profile')
    # Additional info
    alias = models.CharField(u'Pseudónimo', max_length=100, blank = True)
    smial = models.CharField(u'Smial', max_length=100, blank = True)
    phone = models.CharField(u'Teléfono', max_length=100)
    city = models.CharField(u'Población', max_length=100)
    age = models.IntegerField(u'Edad')
    notes_food = models.TextField(u'Comentarios comida', blank = True)  # (vegetariano, celiaco...)
    dinner_menu = models.CharField(u'Menú de la cena de gala', max_length=50, blank = True,
        choices=(
            (u'', u''),
            #(u'ternasco', u'Ternasco asado'),
            #(u'merluza', u'Lomo de merluza en salsa verde con hortalizas'),
            #(u'otros', u'Otros'),
            #(u'sin_cena', u'No voy a ir a la cena de gala'),
        )
    )
    day_1 = models.BooleanField(u'Asistencia viernes/sábado', default=True)
    day_2 = models.BooleanField(u'Asistencia sábado/domingo', default=True)
    day_3 = models.BooleanField(u'Asistencia domingo/lunes+cena', default=True)
    notes_transport = models.TextField(u'Comentarios transporte', blank = True)  # (medio de transporte, hora de llegada...)
    room_choice = models.CharField(u'Elige un tipo de alojamiento', max_length=50,
        choices=(
            (u'inscripcion-completa', u'Inscripción completa'),
            (u'fin-de-semana', u'Fin de semana y cena de gala'),
            #(u'triple-individual', u'Habitación triple - en cama individual'),
            #(u'triple-matrimonio', u'Habitación triple - en cama de matrimonio'),
            #(u'doble-individual', u'Habitación doble - en cama individual'),
            #(u'doble-matrimonio', u'Habitación doble - en cama de matrimonio'),
            (u'sin-alojamiento', u'No voy a pernoctar en el hotel'),
            (u'otros', u'Otros (contactar con la organización)'),
        )
    )
    room_preferences = models.TextField(u'¿Tienes alguna preferencia sobre con quién compartir habitación?', blank = True)
    children_count = models.IntegerField(u'¿Traes niños a tu cargo? Si es así, indica cuántos', default=0)
    children_names = models.TextField(u'Indica sus nombres, uno en cada línea', blank = True)
    is_ste_member = models.BooleanField(u'¿Eres socio/a de la STE?', default=True)
    want_ste_member = models.BooleanField(u'En caso de que no, ¿quieres serlo por 2€ más?', default=False)
    squire = models.BooleanField(u'¿Quieres ser escudero?', default=False)
    notes_general = models.TextField(u'Comentarios general', blank = True)
    shirts_S = models.IntegerField(u'Camisetas talla S', default=0)
    shirts_M = models.IntegerField(u'Camisetas talla M', default=0)
    shirts_L = models.IntegerField(u'Camisetas talla L', default=0)
    shirts_XL = models.IntegerField(u'Camisetas talla XL', default=0)
    shirts_XXL = models.IntegerField(u'Camisetas talla XXL', default=0)
    quota = models.IntegerField(u'Cuota')
    payed = models.IntegerField(u'Pagado')
    payment = models.TextField(u'Estado de pago') # (u'pendiente de pago', u'pago confirmado', <texto de problema>)
    lost = models.CharField(u'(dato interno)', max_length=50, blank=True)   # For lost password recovery

    class Meta:
        verbose_name = u'Ficha de usuario'
        verbose_name_plural = u'Fichas de usuario'
	ordering = ('id',)

    def __unicode__(self):
        return self.user.username + u' - ' + self.user.email + u' - ' + self.user.get_full_name() + u' - ' + self.payment[:40] + u'...'

    @property
    def payment_code(self):
    	return u'EC%d' % (self.user.id + 100)

    @property
    def is_under_age(self):
        return (self.age < 18)

    def get_admin_url(self):
        from django.conf import settings
        from django.core.urlresolvers import reverse
        return settings.PROTOCOL + '://' + settings.SITE_URL + \
                reverse('admin:auth_user_change', args=(self.user.id,))

    def generate_reminder_code(self):
        chars = string.letters + string.digits
        self.lost = ''.join([choice(chars) for i in range(50)])

    def reset_reminder_code(self):
        self.lost = ''


class Activity(models.Model):
    title = models.CharField(u'Título', max_length=100)
    subtitle = models.TextField(u'Entradilla', blank = True)
    text = models.TextField(u'Descripción', blank = True)
    start = models.DateTimeField(u'Empieza en', blank = True, null = True)
    end = models.DateTimeField(u'Termina en', blank = True, null = True)
    duration = models.CharField(u'Duración aproximada', max_length = 50)
    max_places = models.IntegerField(u'Nº máximo de plazas', default = 0)
    logistics = models.TextField(u'Necesidades logísticas', blank = True)
    notes_organization = models.TextField(u'Comentarios', blank = True)
    has_view_page = models.BooleanField(u'Tiene página propia')
    show_owners = models.BooleanField(u'Mostrar responsables')
    requires_inscription = models.BooleanField(u'Requiere inscripción')

    owners = models.ManyToManyField(User, verbose_name = u'Responsables', related_name = 'owner_of')
    organizers = models.ManyToManyField(User,
                                        verbose_name = u'Organizadores',
					related_name = u'organizer_of',
					blank = True)
    participants = models.ManyToManyField(User,
                                          verbose_name = u'Participantes',
					  related_name = u'participant_of',
					  blank = True)

    class Meta:
        verbose_name = u'Actividad'
        verbose_name_plural = u'Actividades'
        ordering = ['start', 'end']

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('activity', kwargs={'activity_id': self.id})

    def day_start(self):
        if self.start == None:
	    return u' SIN HORARIO'
	else:
	    import locale
	    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
	    return self.start.strftime(u'%A').decode('utf-8')

    def hour_start(self):
        if self.start == None:
	    return u''
	elif self.start.hour == 0 and self.start.minute == 0 and self.start.second == 0 and \
	     self.end != None and self.end.hour == 0 and self.end.minute == 0 and self.end.second == 0:
	    return u''
	else:
            return self.start.strftime(u'%H:%M').decode('utf-8')

    def hour_end(self):
        if self.end == None:
	    return u''
	elif self.start != None and self.start.hour == 0 and self.start.minute == 0 and self.start.second == 0 and \
	     self.end.hour == 0 and self.end.minute == 0 and self.end.second == 0:
	    return u''
	else:
            return self.end.strftime('%H:%M').decode('utf-8')

    def __unicode__(self):
        return u'%s %s - %s' % (self.day_start(), self.hour_start(), self.title)

