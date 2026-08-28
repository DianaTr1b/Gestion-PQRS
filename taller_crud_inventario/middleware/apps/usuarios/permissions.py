from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin

def tecnico_required(view_func):
    """
    Decorador que verifica si el usuario tiene rol de Técnico
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder.')
            return redirect('login')
        
        if not hasattr(request.user, 'perfil'):
            messages.error(request, 'Tu usuario no tiene un perfil asignado.')
            return redirect('dashboard')
        
        if request.user.perfil.rol.nombre != 'Técnico':
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


class TecnicoRequiredMixin(AccessMixin):
    """
    Mixin que verifica si el usuario tiene rol de Técnico
    Uso en vistas basadas en clases
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder.')
            return redirect('login')
        
        if not hasattr(request.user, 'perfil'):
            messages.error(request, 'Tu usuario no tiene un perfil asignado.')
            return redirect('dashboard')
        
        if request.user.perfil.rol.nombre != 'Técnico':
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)


def es_tecnico(user):
    """
    Función auxiliar para verificar si un usuario es técnico
    """
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'perfil'):
        return False
    if not user.perfil.rol:
        return False
    return user.perfil.rol.nombre == 'Técnico'


def es_bodega(user):
    """
    Función auxiliar para verificar si un usuario es bodega
    """
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'perfil'):
        return False
    if not user.perfil.rol:
        return False
    return user.perfil.rol.nombre == 'Bodega'


def es_colaborador(user):
    """
    Función auxiliar para verificar si un usuario es colaborador
    """
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'perfil'):
        return False
    if not user.perfil.rol:
        return False
    return user.perfil.rol.nombre == 'Colaborador'

def login_required_custom(view_func):
    """
    Decorador que solo verifica que el usuario esté autenticado y tenga perfil.
    Reemplaza @staff_member_required en vistas accesibles para todos los roles.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder.')
            return redirect('login')
        if not hasattr(request.user, 'perfil'):
            messages.error(request, 'Tu usuario no tiene un perfil asignado.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def colaborador_restringido(view_func):
    """
    Bloquea el acceso a colaboradores y los redirige al dashboard.
    Usar en vistas que colaborador no debe ver.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'perfil') and request.user.perfil.rol and \
                request.user.perfil.rol.nombre == 'Colaborador':
            from django.contrib import messages
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('inventario:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def solo_tecnico(view_func):
    """Solo técnicos pueden acceder. Resto redirige al dashboard con mensaje."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'perfil') or not request.user.perfil.rol:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('inventario:dashboard')
        if request.user.perfil.rol.nombre != 'Técnico':
            messages.error(request, 'Solo el rol Técnico puede acceder a esta sección.')
            return redirect('inventario:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

# def puede_ver_todas_bodegas(user):
#     """
#     Verifica si el usuario puede ver todas las bodegas
#     Solo la bodega principal o técnicos pueden ver todas
#     """
#     if not user.is_authenticated:
#         return False
    
#     if es_tecnico(user):
#         return True
    
#     if es_bodega(user):
#         # Verificar si su bodega es la principal
#         from apps.inventario.models import Bodega
#         try:
#             bodega = Bodega.objects.get(usuario_responsable=user)
#             return bodega.es_bodega_principal
#         except Bodega.DoesNotExist:
#             return False
    
#     return False