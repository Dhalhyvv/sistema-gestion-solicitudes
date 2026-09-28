from django.contrib import admin
from django.urls import path
from usuariosApp import views as vusuarios

urlpatterns = [
    path('', vusuarios.inicio_usuarios, name='usuarios_inicio'),
    path('lista/', vusuarios.lista_usuarios, name='usuarios_lista'),
]
