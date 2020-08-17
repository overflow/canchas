from django.views.generic import ListView

from reservas.models import Reserva


class ClienteProfile(ListView):
    template_name = 'reservas/_list.html'
    def get_queryset(self):
        return Reserva.objects.filter(
                cliente=self.request.user)

