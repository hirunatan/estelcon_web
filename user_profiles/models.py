from django.db import models
from django.contrib.auth.models import User

from random import choice
import string


class UserProfile(models.Model):
    # Link with the Django user
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)

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
                'Habitación compartida', (
                    ('compartida-completa', '(compartida) completa'),
                    ('compartida-v-a-d', '(compartida) viernes a domingo'),
                    ('compartida-s-y-d', '(compartida) sábado y domingo'),
                )
            ),(
                'Habitación individual', (
                    ('individual-completa', '(individual) completa'),
                    ('individual-v-a-d', '(individual) viernes a domingo'),
                    ('individual-s-y-d', '(individual) sábado y domingo'),
                )
            ),
            ('otros', 'Otros'),
        )
    )
    room_preferences = models.TextField('¿Tienes alguna preferencia sobre con quién compartir habitación?', blank = True)
    children_count = models.IntegerField('¿Traes niños a tu cargo? Si es así, indica cuántos', default=0)
    children_names = models.TextField('Indica sus nombres, uno en cada línea', blank = True)
    is_ste_member = models.BooleanField('¿Eres socio/a de la STE?', default=True)
    want_ste_member = models.BooleanField('En caso de que no, ¿quieres asociarte por 12€ más?', default=False)
    squire = models.BooleanField('¿Quieres ser escudero?', default=False)
    first_estelcon = models.BooleanField('¿Es tu primera Estelcon?', default=False)
    want_mentor = models.BooleanField('¿Querrías participar en el programa de mentorazgo a nuevos asistentes?', default=False)
    want_media = models.BooleanField('Autorizo el uso de material audiovisual generado durante el evento Mereth Aderthad 2019 en donde se me pueda identificar por parte de la Sociedad Tolkien Española en su labor de difusión de actividades', default=False)
    notes_general = models.TextField('Comentarios general', blank = True)
    shirts_S_1 = models.IntegerField('Camisetas talla S (1)', default=0)
    shirts_M_1 = models.IntegerField('Camisetas talla M (1)', default=0)
    shirts_L_1 = models.IntegerField('Camisetas talla L (1)', default=0)
    shirts_XL_1 = models.IntegerField('Camisetas talla XL (1)', default=0)
    shirts_XXL_1 = models.IntegerField('Camisetas talla XXL (1)', default=0)
    shirts_S_2 = models.IntegerField('Camisetas talla S (2)', default=0)
    shirts_M_2 = models.IntegerField('Camisetas talla M (2)', default=0)
    shirts_L_2 = models.IntegerField('Camisetas talla L (2)', default=0)
    shirts_XL_2 = models.IntegerField('Camisetas talla XL (2)', default=0)
    shirts_XXL_2 = models.IntegerField('Camisetas talla XXL (2)', default=0)
    shirts_S_3 = models.IntegerField('Camisetas talla S (3)', default=0)
    shirts_M_3 = models.IntegerField('Camisetas talla M (3)', default=0)
    shirts_L_3 = models.IntegerField('Camisetas talla L (3)', default=0)
    shirts_XL_3 = models.IntegerField('Camisetas talla XL (3)', default=0)
    shirts_XXL_3 = models.IntegerField('Camisetas talla XXL (3)', default=0)
    quota = models.IntegerField('Cuota')
    payed = models.IntegerField('Pagado')
    payment = models.TextField('Estado de pago') # (u'pendiente de pago', u'pago confirmado', <texto de problema>)
    lost = models.CharField('(dato interno)', max_length=50, blank=True)   # For lost password recovery

    class Meta:
        verbose_name = 'Ficha de usuario'
        verbose_name_plural = 'Fichas de usuario'
        ordering = ('id',)

    def __str__(self):
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
        chars = string.ascii_letters + string.digits
        self.lost = ''.join([choice(chars) for i in range(50)])

    def reset_reminder_code(self):
        self.lost = ''

