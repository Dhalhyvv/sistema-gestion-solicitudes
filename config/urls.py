from django.urls import include, path
from django.views.generic import RedirectView

# Sin Django Admin: toda la gestión se hace con vistas y templates propios.
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False), name='inicio'),
    path('', include('usuariosApp.urls')),
    path('solicitudes/', include('solicitudesApp.urls')),
]

handler403 = 'usuariosApp.views.error_403'
