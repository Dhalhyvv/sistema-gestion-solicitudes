from django.urls import path

from . import views

urlpatterns = [
    # Mantenedor de solicitudes
    path('', views.SolicitudLista.as_view(), name='solicitud_lista'),
    path('nueva/', views.SolicitudCrear.as_view(), name='solicitud_crear'),
    path('<int:pk>/', views.SolicitudDetalle.as_view(), name='solicitud_detalle'),
    path('<int:pk>/editar/', views.SolicitudEditar.as_view(), name='solicitud_editar'),
    path('<int:pk>/eliminar/', views.SolicitudEliminar.as_view(), name='solicitud_eliminar'),

    # Transacción: registro de atención
    path('atenciones/', views.AtencionLista.as_view(), name='atencion_lista'),
    path('atenciones/nueva/', views.atencion_nueva, name='atencion_nueva'),
    path('<int:pk>/atender/', views.atencion_nueva, name='atencion_solicitud'),

    # Mantenedor de delegaciones
    path('delegaciones/', views.DelegacionLista.as_view(), name='delegacion_lista'),
    path('delegaciones/nueva/', views.DelegacionCrear.as_view(), name='delegacion_crear'),
    path('delegaciones/<int:pk>/editar/', views.DelegacionEditar.as_view(), name='delegacion_editar'),
    path('delegaciones/<int:pk>/eliminar/', views.DelegacionEliminar.as_view(), name='delegacion_eliminar'),

    # Mantenedor de categorías
    path('categorias/', views.CategoriaLista.as_view(), name='categoria_lista'),
    path('categorias/nueva/', views.CategoriaCrear.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaEditar.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaEliminar.as_view(), name='categoria_eliminar'),
]
