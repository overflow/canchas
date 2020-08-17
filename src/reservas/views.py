from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
        DeleteView,
        DetailView,
        FormView,
        ListView)
from django.views.generic import View
from django.views.generic.edit import FormMixin, UpdateView
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse

from reservas.forms import SelectFechaForm, SelectHoraForm
from reservas.models import Horario, Reserva, Reservado


class HorarioView(FormMixin, ListView):
    """
    Muestra Horarios de la reserva y permite agregar uno nuevo
    """
    form_class = SelectFechaForm
    template_name = 'reservas/_fecha_form.html'

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        Si el formulario es valido redirigir a vista para seleccionar
        entre las horas disponibles 
        """

        return HttpResponseRedirect(reverse('reserva_hora', kwargs={
            'dia': form.cleaned_data['fecha'].day,
            'mes': form.cleaned_data['fecha'].month,
            'anio': form.cleaned_data['fecha'].year,
            'cancha': form.cleaned_data['cancha']}))

    def get_queryset(self):
        reserva = self.request.user.reserva
        if reserva:
            return Reservado.objects.filter(
                    reserva=reserva,
                    reserva__completada=False)
        else:
            return Horario.objects.none()


class AddHoraView(FormMixin, ListView):
    """
    Agrega Horario
    """
    form_class = SelectHoraForm
    template_name = 'reservas/_hora_form.html'

    def form_valid(self, form):
        return HttpResponseRedirect(reverse('reserva_fecha'))

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)


    def get_form_kwargs(self):
        """
        Pasa los parametros para configurar el formulario
        y para crear el horario al procesarlo
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['cancha'] = self.kwargs.get('cancha')
        kwargs['horas'] = Horario.get_horas_disponibles(
                cancha = self.kwargs.get('cancha'),
                dia = self.kwargs.get('dia'),
                mes = self.kwargs.get('mes'),
                anio = self.kwargs.get('anio'),
                )
        kwargs['fecha'] = '{dia}-{mes}-{anio}'.format(**self.kwargs)
        return kwargs 

    def get_queryset(self):
        """
        Listar las horas registradas en la reserva
        """
        reserva = self.request.user.reserva
        if reserva:
            return Reservado.objects.filter(
                    reserva=reserva,
                    reserva__completada=False)
        else:
            return Horario.objects.none()

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context.update({
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            })
        else:
            context.update({
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            })
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        for cancha, nombre in Horario.CANCHAS:
            if cancha == self.kwargs.get('cancha'):
                cancha =  nombre
                break
        context['cancha'] = cancha
        context['fecha'] = '{dia}/{mes}/{anio}'.format(
                **self.kwargs)
            
        return context 

    def post(self, request, *args, **kwargs):
        """
        Obtiene la lista de horas registradas para la reserva
        Valida formulario
        """
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class HorarioDeleteView(DeleteView):
    """
    Eliminar horas de la reserva
    """
    template_name = 'reservas/_delete.html'
    success_url = reverse_lazy('reserva_fecha')

    def get_queryset(self):
        return Horario.objects.filter(
                reservado__reserva=self.request.user.reserva)


class ReservaCompletarView(View):
    """
    Marca una Reserva como completada
    """
    
    def get(self, request, *args, **kwargs):
        reserva = self.request.user.reserva
        if reserva:
            reserva.completada = True
            reserva.save()
        return HttpResponseRedirect(reverse('account_profile'))


class ReservaDeleteView(DeleteView):
    """
    Cancelar una reserva
    """
    template_name = 'reservas/_delete.html'
    success_url = reverse_lazy('account_profile')

    def get_queryset(self):
        """
        Filtra por las reservas del usuario
        """
        return Reserva.objects.filter(
                cliente=self.request.user)

    def get_object(self):
        """
        Valida que la reserva sea cancelable
        """
        reserva = super().get_object()
        print('asdadasdasdasd', reserva)
        if not reserva.cancelable:
            raise Http404
        return reserva

    

class ReservaDetailView(DetailView):
    template_name = 'reservas/_details.html'

    def get_queryset(self):
        return Reserva.objects.filter(
                cliente=self.request.user).order_by('reservado__horario__cancha')

