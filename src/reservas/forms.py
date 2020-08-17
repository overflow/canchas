from django import forms
from django.utils import timezone

from reservas.models import Horario

from bootstrap_datepicker_plus import DatePickerInput
import holidays


class SelectFechaForm(forms.Form):
    fecha = forms.DateField(
            label="Fecha",
            widget=DatePickerInput(format='%d/%m/%Y')
            )
    cancha = forms.ChoiceField(choices=Horario.CANCHAS)

    def clean_fecha(self):
        feriados = holidays.CountryHoliday('CL')
        if self.cleaned_data['fecha'] in feriados:
            raise forms.ValidationError('Fecha es feriada')
        return self.cleaned_data['fecha']


class SelectHoraForm(forms.Form):
    hora = forms.ChoiceField(label='Horas Disponibles', choices=[])

    def __init__(self, *args, **kwargs):
        horas = kwargs.pop('horas')
        self.fecha = kwargs.pop('fecha')
        self.user = kwargs.pop('user')
        self.cancha = kwargs.pop('cancha')
        horas_value = [[hora, hora] for hora in horas]
        super().__init__(*args, **kwargs)
        self.fields['hora'].choices = horas_value

    def clean(self):
        horario = Horario.objects.create(
                cancha=self.cancha,
                fecha=timezone.datetime.strptime(
                    self.fecha+" "+self.cleaned_data['hora'],
                    '%d-%m-%Y %H:%M'))

        self.user.agregar_reserva(horario)
        return super().clean()

