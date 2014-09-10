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
    payment = models.TextField(u'Estado de pago') # (u'pendiente de pago', u'pago confirmado', <texto de problema>)
    notes_food = models.TextField(u'Comentarios comida', blank = True)  # (vegetariano, celiaco...)
    notes_transport = models.TextField(u'Comentarios transporte', blank = True)  # (medio de transporte, hora de llegada...)
    notes_general = models.TextField(u'Comentarios general', blank = True)
    dinner_menu = models.CharField(u'Menú de la cena de gala', max_length=50, choices=((u'carne',u'carne'), (u'pescado',u'pescado'), (u'otros',u'otros')))
    shirts_S = models.IntegerField(u'Camisetas talla S')
    shirts_M = models.IntegerField(u'Camisetas talla M')
    shirts_L = models.IntegerField(u'Camisetas talla L')
    shirts_XL = models.IntegerField(u'Camisetas talla XL')
    shirts_XXL = models.IntegerField(u'Camisetas talla XXL')
    day_1 = models.BooleanField(u'Asistencia jueves/viernes')
    day_2 = models.BooleanField(u'Asistencia viernes/sábado')
    day_3 = models.BooleanField(u'Asistencia sábado/domingo+cena')
    quota = models.IntegerField(u'Cuota')
    payed = models.IntegerField(u'Pagado')
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
    duration = models.CharField(u'Duración aproximada', max_length=50)
    max_places = models.IntegerField(u'Nº máximo de plazas')
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
        return reverse('activity', kwargs={'activity_id': self.id})

    def day_start(self):
        if self.start == None:
	    return u' SIN HORARIO'
	else:
	    #import locale
	    #locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
	    return self.start.strftime('%A')

    def hour_start(self):
        if self.start == None:
	    return ''
	elif self.start.hour == 0 and self.start.minute == 0 and self.start.second == 0 and \
	     self.end != None and self.end.hour == 0 and self.end.minute == 0 and self.end.second == 0:
	    return ''
	else:
            return self.start.strftime('%H:%M')

    def hour_end(self):
        if self.end == None:
	    return ''
	elif self.start != None and self.start.hour == 0 and self.start.minute == 0 and self.start.second == 0 and \
	     self.end.hour == 0 and self.end.minute == 0 and self.end.second == 0:
	    return ''
	else:
            return self.end.strftime('%H:%M')

    def __unicode__(self):
        return u'%s %s - %s' % (self.day_start(), self.hour_start(), self.title)

