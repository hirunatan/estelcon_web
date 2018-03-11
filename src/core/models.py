# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from random import choice
import string


class UserProfile(models.Model):
    # Link with the Django user
    user = models.OneToOneField(User, related_name='profile')
    # Additional info
    alias = models.CharField('pseudónimo', max_length=100, blank = True)
    smial = models.CharField('smial', max_length=100, blank = True)
    phone = models.CharField('teléfono', max_length=100)
    city = models.CharField('población', max_length=100)
    age = models.IntegerField('edad')
    dinner_menu = models.CharField('Menú de la cena de gala', max_length=50, blank = True,
        choices=(
            ('carne', 'Carne'),
            ('pescado', 'Pescado'),
            ('otros', 'Otros'),
            ('sin-cena', 'No voy a ir a la cena de gala'),
        )
    )
    notes_food = models.TextField('Comentarios comida', blank = True)  # (vegetariano, celiaco...)
    day_1 = models.BooleanField('Asistencia viernes/sábado', default=True)
    day_2 = models.BooleanField('Asistencia sábado/domingo', default=True)
    day_3 = models.BooleanField('Asistencia domingo/lunes+cena', default=True)
    notes_transport = models.TextField('Comentarios transporte', blank = True)  # (medio de transporte, hora de llegada...)
    room_choice = models.CharField('Elige un tipo de alojamiento', max_length=50,
        choices=(
            (
                'Albergue (litera y baño comunitario)', (
                    ('albergue-completa', '(litera) completa'),
                    ('albergue-v-a-d', '(litera) viernes a domingo'),
                    ('albergue-s-y-d', '(litera) sábado y domingo'),
                )
            ),(
                'Habitación doble con baño propio', (
                    ('doble-completa', '(doble) completa'),
                    ('doble-v-a-d', '(doble) viernes a domingo'),
                    ('doble-s-y-d', '(doble) sábado y domingo'),
                )
            ),
            ('sin-alojamiento', 'No voy a pernoctar en el seminario'),
            ('otros', 'Otros'),
        )
    )
    room_preferences = models.TextField('¿Tienes alguna preferencia sobre con quién compartir habitación?', blank = True)
    children_count = models.IntegerField('¿Traes niños a tu cargo? Si es así, indica cuántos', default=0)
    children_names = models.TextField('Indica sus nombres, uno en cada línea', blank = True)
    is_ste_member = models.BooleanField('¿Eres socio/a de la STE?', default=True)
    want_ste_member = models.BooleanField('En caso de que no, ¿quieres asociarte por 2€ más?', default=False)
    squire = models.BooleanField('¿Quieres ser escudero?', default=False)
    first_estelcon = models.BooleanField('¿Es tu primera Estelcon?', default=False)
    want_boat = models.BooleanField('¿Quieres remontar en barco por el río?', default=False)
    notes_general = models.TextField('Comentarios general', blank = True)
    shirts_S = models.IntegerField('Camisetas talla S', default=0)
    shirts_M = models.IntegerField('Camisetas talla M', default=0)
    shirts_L = models.IntegerField('Camisetas talla L', default=0)
    shirts_XL = models.IntegerField('Camisetas talla XL', default=0)
    shirts_XXL = models.IntegerField('Camisetas talla XXL', default=0)
    quota = models.IntegerField('Cuota')
    payed = models.IntegerField('Pagado')
    payment = models.TextField('Estado de pago') # (u'pendiente de pago', u'pago confirmado', <texto de problema>)
    lost = models.CharField('(dato interno)', max_length=50, blank=True)   # For lost password recovery

    class Meta:
        verbose_name = 'Ficha de usuario'
        verbose_name_plural = 'Fichas de usuario'
        ordering = ('id',)

    def __unicode__(self):
        return self.user.username + ' - ' + self.user.email + ' - ' + self.user.get_full_name() + ' - ' + self.payment[:40] + '...'

    @property
    def payment_code(self):
        return 'EC%d' % (self.user.id + 100)

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
    title = models.CharField('Título', max_length=100)
    subtitle = models.TextField('Entradilla', blank = True)
    text = models.TextField('Descripción', blank = True)
    start = models.DateTimeField('Empieza en', blank = True, null = True)
    end = models.DateTimeField('Termina en', blank = True, null = True)
    duration = models.CharField('Duración aproximada', max_length = 50)
    max_places = models.IntegerField('Nº máximo de plazas', default = 0)
    logistics = models.TextField('Necesidades logísticas', blank = True)
    notes_organization = models.TextField('Comentarios', blank = True)
    has_view_page = models.BooleanField('Tiene página propia', default = False)
    show_owners = models.BooleanField('Mostrar responsables', default = False)
    requires_inscription = models.BooleanField('Requiere inscripción', default = False)

    owners = models.ManyToManyField(User, verbose_name = 'Responsables', related_name = 'owner_of')
    organizers = models.ManyToManyField(User,
                                        verbose_name = 'Organizadores',
                                        related_name = 'organizer_of',
                                        blank = True)
    participants = models.ManyToManyField(User,
                                          verbose_name = 'Participantes',
                                          related_name = 'participant_of',
                                          blank = True)

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['start', 'end']

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('activity', kwargs={'activity_id': self.id})

    def day_start(self):
        if self.start == None:
            return ' SIN HORARIO'
        else:
            import locale
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
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
        return '%s %s - %s' % (self.day_start(), self.hour_start(), self.title)

