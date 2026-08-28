from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Panel de administración
    path('', views.admin_panel, name='admin_panel'),
    
    # Usuarios
    path('usuarios/', views.usuarios_lista, name='usuarios_lista'),
    path('usuarios/crear/', views.usuario_crear, name='usuario_crear'),
    path('usuarios/<int:usuario_id>/', views.usuario_detalle, name='usuario_detalle'),
    path('usuarios/<int:usuario_id>/editar/', views.usuario_editar, name='usuario_editar'),
    
    # Roles
    path('roles/', views.roles_lista, name='roles_lista'),
    path('roles/crear/', views.rol_crear, name='rol_crear'),
    path('roles/<int:rol_id>/editar/', views.rol_editar, name='rol_editar'),
    
    # Categorías
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:categoria_id>/editar/', views.categoria_editar, name='categoria_editar'),
    # Talento
    path('webhook/', views.webhook_gestion_humana, name='webhook_gh'),
]