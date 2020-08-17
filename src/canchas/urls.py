from django.contrib.auth import views as auth_views
from django .contrib.auth.decorators import login_required
from django.urls import path

from reservas.views import (
        AddHoraView,
        HorarioView,
        HorarioDeleteView,
        ReservaDeleteView,
        ReservaDetailView,
        ReservaCompletarView)
from usuarios.views import ClienteProfile


urlpatterns = [
    path('', login_required(ClienteProfile.as_view()), name='index'),
    path('accounts/login/', auth_views.LoginView.as_view()),
    path('accounts/profile/', login_required(ClienteProfile.as_view()), name='account_profile'),

    path('reservas/fecha/', login_required(HorarioView.as_view()), name='reserva_fecha'),
    path('reservas/hora/<int:dia>/<int:mes>/<int:anio>/<str:cancha>/', login_required(AddHoraView.as_view()), name='reserva_hora'),
    path('reservas/hora/<int:pk>/eliminar', login_required(HorarioDeleteView.as_view()), name='horario_delete'), 
    path('reservas/<int:pk>/cancelar', login_required(HorarioDeleteView.as_view()), name='horario_delete'),
    path('reservas/completar', login_required(ReservaCompletarView.as_view()), name='reserva_completar'),
    path('reservas/<int:pk>/delete', login_required(ReservaDeleteView.as_view()), name='reserva_delete'),
    path('reservas/<int:pk>/', login_required(ReservaDetailView.as_view()), name='reserva_detail')
]
