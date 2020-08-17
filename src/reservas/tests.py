from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Horario, Reserva, Reservado

User = get_user_model()

class ReservasTestCase(TestCase):
    def setUp(self):
        self.usuario = User.objects.create(email='foobar@gmail.com')

    def test_disponibilidad_horario(self):
        """
        Validar que los horarios reservados no estan disponibles
        """

        # GIVEN una reserva hoy a las 13:30 no completada
        horario = Horario.objects.create(
                fecha=timezone.datetime(
                    day=timezone.now().day,
                    month=timezone.now().month,
                    year=timezone.now().year,
                    hour=13,
                    minute=30),
                cancha=Horario.BABY)

        reserva = Reserva.objects.create(
                cliente=self.usuario,
                fecha=timezone.now())

        reservado = Reservado.objects.create(
                reserva=reserva,
                horario=horario)

        # WHEN un usuario consulta las horas disponibles 
        horarios = Horario.get_horas_disponibles(
                cancha=Horario.BABY)

        # THEN ese horario sigue disponible
        self.assertTrue('13:30' in horarios)

        # WHEN la reserva esta completada
        reserva.completada = True
        reserva.save()

        # THEN ese horario no estará disponible
        horarios = Horario.lista_horas_disponibles(
                cancha=Horario.BABY)
        self.assertTrue('13:30' not in horarios)


    def test_limite_reservas(self):
        """
        Validar que solo se puede reservar maximo 2 horas
        """

        # GIVEN varios horarios
        horarios =[Horario(
                fecha=timezone.datetime(
                day=timezone.now().day,
                month=timezone.now().month,
                year=timezone.now().year,
                hour=h,
                minute=30),
                cancha=Horario.BABY) for h in range(13,18)]
        Horario.objects.bulk_create(horarios)

        # WHEN se van a reservar
        for horario in horarios[:-1]:
            self.usuario.agregar_reserva(horario)
            
        # THEN no se pueden registrar mas de dos horas
        self.assertRaises(ValidationError, self.usuario.agregar_reserva, horarios[-1])

    def test_cancelar_reserva(self):
        """
        Validar que no se puede cancelar reserva luego de 12 horas
        """

        #GIVEN un horario
        horario = Horario.objects.create(
                fecha=timezone.datetime(
                    day=timezone.now().day,
                    month=timezone.now().month,
                    year=timezone.now().year,
                    hour=13,
                    minute=30),
                cancha=Horario.BABY)

        reserva = Reserva.objects.create(
                cliente=self.usuario,
                )
        reserva.fecha = timezone.now()-timezone.timedelta(hours=12)

        self.usuario.agregar_reserva(horario)

        # WHEN se completa una reserva
        reserva.completada = True
        reserva.save()

        # THEN se intenta cancelar la reserva no puede ser mayor de 12 horas
        self.assertRaises(ValidationError, self.usuario.cancelar_reserva, reserva)

        # WHEN la fecha de la reserva es menor a 12 horas
        reserva.fecha = timezone.now()-timezone.timedelta(hours=11)

        # THEN la reserva se puede cancelar
        id = reserva.id
        self.usuario.cancelar_reserva(reserva)
        self.assertFalse(Reserva.objects.filter(id=id).exists())
