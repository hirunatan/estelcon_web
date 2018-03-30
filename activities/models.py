from django.db import models

from user_profiles.models import User


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

    def __str__(self):
        return '%s %s - %s' % (self.day_start(), self.hour_start(), self.title)

