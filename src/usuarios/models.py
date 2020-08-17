from django.contrib.auth.models import AbstractUser, BaseUserManager

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.functional import cached_property


class UserProfileManager(BaseUserManager):
    """Model manager for customized user model UserProfile"""
    def create_user(self, email, password, **kwargs):
        """Create a new user profile with no special permissions."""
        if not email:
            raise ValueError("A user must have an email address!")

        if not email:
            raise ValueError("A user must have a email!")

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            user.is_active = False
        user.username =email 
        user.email = email
        user.is_active = True

        user.save()

        return user

    def create_superuser(self, email, password):
        """Create a new super user"""
        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True
        user.is_active = True

        user.save()

        return user


class Cliente(AbstractUser):
    email = models.EmailField('email address', unique=True)
    objects = UserProfileManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    @cached_property
    def reserva(self):
        """"
        Obtiene reserva abierta (no completada)
        """

        from reservas.models import Reserva
        return Reserva.objects.filter(
                cliente=self,
                completada=False).last()


    def agregar_reserva(self, horario):
        """
        Se registra un horario a una reserva no completada
        """

        from reservas.models import Reserva

        reserva, new = Reserva.objects.get_or_create(
                cliente=self,
                completada=False
                )
        reserva.agregar_horario(horario)
        return reserva

    def cancelar_reserva(self, reserva):
        from reservas.models import Horario
        """
        Se cancela la reserva 
        """

        if reserva.completada:
            if timezone.now() - reserva.fecha > timezone.timedelta(hours=12):
                raise ValidationError('No se puede cancelar una reserva despues de 12 horas')

        # Eliminar los horarios asociados a la reserva
        Horario.objects.filter(reservado__reserva=reserva).delete()
        reserva.delete()



