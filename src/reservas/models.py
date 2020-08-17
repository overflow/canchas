from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

import datetime
import time

User = get_user_model()

#HORAS = ['%s:%s%s' % (h, m, ap) for ap in ('am', 'pm') for h in ([12] + list(range(1,12))) for m in ('00', '30')]
HORAS = ['%s:%s' % (h, m) for h in ([12] + list(range(9,22))) for m in ('00', '30')][:-1]


class Horario(models.Model):
                    

    BABY = 'baby'
    CANCHA_BABY = (BABY, 'Cancha de Baby')
    GIMNASIO = 'gym'
    CANCHA_GIMNASIO = (GIMNASIO, 'Cancha de gimnasio')
    PASTO = 'pasto'
    CANCHA_PASTO = (PASTO, 'Cancha de Pasto')

    CANCHAS = (
            CANCHA_PASTO,
            CANCHA_BABY,
            CANCHA_GIMNASIO)

    fecha = models.DateTimeField(db_index=True)
    cancha = models.CharField(max_length=5, choices=CANCHAS, db_index=True)

    @cached_property
    def finalizacion(self):
        """
        Retorna la fecha de inicio del horario reservado mas 30 minutos
        """
        return self.fecha + timezone.timedelta(minutes=30)

    @classmethod
    def get_horas_disponibles(
            self,
            cancha,
            dia=timezone.now().day,
            mes=timezone.now().month,
            anio=timezone.now().year):
        """
        Retorna horas disponibles para la cancha/fecha
        """

        no_disponible = Reservado.objects.filter(
                horario__cancha=cancha,
                horario__fecha__day=dia,
                horario__fecha__month=mes,
                horario__fecha__year=anio).order_by('horario__fecha__hour', 'horario__fecha__minute')

        # Descarta las horas reservadas y ordena
        return [time.strftime('%H:%M', x) for x in  sorted(time.strptime(t, '%H:%M') for t in filter(lambda x, no_disponible=no_disponible: not no_disponible.filter(horario__fecha__hour=x.split(':')[0], horario__fecha__minute=x.split(':')[1]).exists(), HORAS))]

    @cached_property
    def monto(self):
        return Reserva.COSTOS[self.cancha]


class Reserva(models.Model):
    COSTOS = {
            Horario.BABY: 10000,
            Horario.PASTO: 13000,
            Horario.GIMNASIO: 8000
            }
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    # Una reserva completada no se puede modificar
    completada = models.BooleanField(default=False)


    @cached_property
    def cancelable(self):
        return timezone.now() - self.fecha < timezone.timedelta(hours=12)

    @cached_property
    def monto(self):
        total = 0
        for reserva in self.reservado_set.all():
            total += self.COSTOS[reserva.horario.cancha]

        return total


    def agregar_horario(self, horario):
        """
        Agrega un horario a la reserva mientras  el total
        de horas reservadas no sea mayor a 2 horas (4 horarios)
        """

        reservados = Reservado.objects.filter(reserva=self)
        
        if self.completada:
            raise ValidationError(
                    'No se pueden modificar reservas completadas')
        if reservados.exists() and reservados.count() == 4:
            raise ValidationError(
                    'No se puede registrar mas de 2 horas por reserva')
    
        Reservado.objects.create(
                reserva=self,
                horario=horario)


class Reservado(models.Model):
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
