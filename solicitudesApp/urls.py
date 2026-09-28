from django.urls import path
from solicitudesApp import views as vsolicitudes

urlpatterns = [
    path('', vsolicitudes.inicio_solicitudes, name='solicitudes_inicio'),
    path('lista/', vsolicitudes.lista_solicitudes, name='solicitudes_lista'),
]
