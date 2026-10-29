from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Recuperación de contraseña por correo (token seguro de Django)
    path('recuperar/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.txt',
        subject_template_name='registration/password_reset_subject.txt',
    ), name='password_reset'),
    path('recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('recuperar/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Dashboard según perfil
    path('dashboard/', views.dashboard, name='dashboard'),

    # Mantenedor de funcionarios
    path('funcionarios/', views.FuncionarioLista.as_view(), name='funcionario_lista'),
    path('funcionarios/nuevo/', views.FuncionarioCrear.as_view(), name='funcionario_crear'),
    path('funcionarios/<int:pk>/editar/', views.FuncionarioEditar.as_view(), name='funcionario_editar'),
    path('funcionarios/<int:pk>/eliminar/', views.FuncionarioEliminar.as_view(), name='funcionario_eliminar'),

    # Gestión de usuarios del sistema (solo Administrador)
    path('cuentas/', views.CuentaLista.as_view(), name='cuenta_lista'),
    path('cuentas/nueva/', views.CuentaCrear.as_view(), name='cuenta_crear'),
    path('cuentas/<int:pk>/editar/', views.CuentaEditar.as_view(), name='cuenta_editar'),
    path('cuentas/<int:pk>/eliminar/', views.CuentaEliminar.as_view(), name='cuenta_eliminar'),
]
