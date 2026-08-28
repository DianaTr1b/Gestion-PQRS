from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import PerfilUsuario, Rol
from django.contrib.auth.models import User
from .forms import UsuarioForm, RolForm, CategoriaForm
from apps.inventario.models import Categoria


# ===================== PANEL DE ADMINISTRACIÓN =====================

@staff_member_required
def admin_panel(request):
    """Panel principal de administración"""
    # Estadísticas
    total_usuarios = User.objects.count()
    total_roles = Rol.objects.count()
    total_categorias = Categoria.objects.count()
    
    
    # Últimos registros
    ultimos_usuarios = PerfilUsuario.objects.order_by('-id')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_roles': total_roles,
        'total_categorias': total_categorias,
        'ultimos_usuarios': ultimos_usuarios,
    }
    
    return render(request, 'apps/usuarios/admin_panel.html', context)


# ===================== USUARIOS - CRUD =====================

@staff_member_required
def usuarios_lista(request):
    """Lista todos los usuarios"""
    usuarios = PerfilUsuario.objects.select_related('rol').order_by('-id')
    
    # Filtros
    busqueda = request.GET.get('q')
    estado_filtro = request.GET.get('estado')
    rol_filtro = request.GET.get('rol')
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(nombre__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(cargo__icontains=busqueda)
        )
    
    if estado_filtro:
        usuarios = usuarios.filter(estado=estado_filtro)
    
    if rol_filtro:
        usuarios = usuarios.filter(rol_id=rol_filtro)
    
    roles = Rol.objects.all()
    
    context = {
        'usuarios': usuarios,
        'roles': roles,
        'busqueda': busqueda,
        'estado_filtro': estado_filtro,
        'rol_filtro': rol_filtro,
    }
    
    return render(request, 'apps/usuarios/usuarios/lista.html', context)


@staff_member_required
def usuario_crear(request):
    """Crear un nuevo usuario"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario "{usuario.nombre}" creado exitosamente.')
            return redirect('usuarios:usuarios_lista')
    else:
        form = UsuarioForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Usuario',
        'accion': 'Crear'
    }
    
    return render(request, 'apps/usuarios/usuarios/formulario.html', context)


@staff_member_required
def usuario_editar(request, usuario_id):
    """Editar un usuario existente"""
    usuario = get_object_or_404(PerfilUsuario, id=usuario_id)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario "{usuario.nombre}" actualizado exitosamente.')
            return redirect('usuarios:usuarios_lista')
    else:
        form = UsuarioForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': f'Editar: {usuario.nombre}',
        'accion': 'Actualizar'
    }
    
    return render(request, 'apps/usuarios/usuarios/formulario.html', context)


@staff_member_required
def usuario_detalle(request, usuario_id):
    """Ver detalle de un usuario"""
    usuario = get_object_or_404(
        PerfilUsuario.objects.select_related('rol'),
        id=usuario_id
    )
    
    # Elementos asignados actualmente
    from apps.inventario.models import Elemento
    elementos_asignados = Elemento.objects.filter(
        usuario_actual=usuario,
        estado='Asignado'
    ).select_related('categoria', 'bodega_actual')
    
    # Historial de elementos
    from apps.inventario.models import DetalleMovimiento
    historial_elementos = DetalleMovimiento.objects.filter(
        usuario_actual=usuario
    ).select_related('elemento', 'movimiento').order_by('-movimiento__fecha_movimiento')[:10]
    
    context = {
        'usuario': usuario,
        'elementos_asignados': elementos_asignados,
        'historial_elementos': historial_elementos,
    }
    
    return render(request, 'apps/usuarios/usuarios/detalle.html', context)


# ===================== ROLES - CRUD =====================

@staff_member_required
def roles_lista(request):
    """Lista todos los roles"""
    roles = Rol.objects.annotate(
        total_usuarios=Count('usuarios')
    ).order_by('nombre')
    
    context = {
        'roles': roles,
    }
    
    return render(request, 'apps/usuarios/roles/lista.html', context)


@staff_member_required
def rol_crear(request):
    """Crear un nuevo rol"""
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            rol = form.save()
            messages.success(request, f'Rol "{rol.nombre}" creado exitosamente.')
            return redirect('usuarios:roles_lista')
    else:
        form = RolForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Rol',
        'accion': 'Crear'
    }
    
    return render(request, 'apps/usuarios/roles/formulario.html', context)


@staff_member_required
def rol_editar(request, rol_id):
    """Editar un rol existente"""
    rol = get_object_or_404(Rol, id=rol_id)
    
    if request.method == 'POST':
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            rol = form.save()
            messages.success(request, f'Rol "{rol.nombre}" actualizado exitosamente.')
            return redirect('usuarios:roles_lista')
    else:
        form = RolForm(instance=rol)
    
    context = {
        'form': form,
        'rol': rol,
        'titulo': f'Editar: {rol.nombre}',
        'accion': 'Actualizar'
    }
    
    return render(request, 'apps/usuarios/roles/formulario.html', context)


# ===================== CATEGORÍAS - CRUD =====================

@staff_member_required
def categorias_lista(request):
    """Lista todas las categorías"""
    categorias = Categoria.objects.annotate(
        total_elementos=Count('elementos')
    ).order_by('nombre')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'apps/usuarios/categorias/lista.html', context)


@staff_member_required
def categoria_crear(request):
    """Crear una nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('usuarios:categorias_lista')
    else:
        form = CategoriaForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nueva Categoría',
        'accion': 'Crear'
    }
    
    return render(request, 'apps/usuarios/categorias/formulario.html', context)


@staff_member_required
def categoria_editar(request, categoria_id):
    """Editar una categoría existente"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente.')
            return redirect('usuarios:categorias_lista')
    else:
        form = CategoriaForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria,
        'titulo': f'Editar: {categoria.nombre}',
        'accion': 'Actualizar'
    }
    
    return render(request, 'apps/usuarios/categorias/formulario.html', context)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json


def validar_webhook_gestion_humana(request):
    """Valida que el webhook viene de Gestión Humana"""
    client_id = request.headers.get('X-Client-ID')

    if not client_id or client_id != settings.GESTION_HUMANA_CLIENT_ID:
        return False

    return True


@csrf_exempt
@require_http_methods(["POST"])
def webhook_gestion_humana(request):
    """
    Receptor de webhooks de Gestión Humana.
    URL que le darás a GH: http://tu-sistema/api/usuarios/webhook/
    """

    # 1. Validar autenticación
    if not validar_webhook_gestion_humana(request):
        return JsonResponse({'error': 'No autorizado'}, status=401)

    # 2. Parsear webhook
    try:
        data = json.loads(request.body)
        evento = data.get('evento')
        usuario_data = data.get('usuario', {})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    # 3. Procesar evento
    try:
        if evento in ['usuario.creado', 'usuario.actualizado']:
            mensaje = sincronizar_usuario_desde_gh(usuario_data)

        elif evento == 'usuario.password_cambiado':
            mensaje = cerrar_sesiones_usuario_gh(usuario_data['id'])

        elif evento == 'usuario.eliminado':
            mensaje = desactivar_usuario_gh(usuario_data['id'])

        else:
            return JsonResponse({'error': f'Evento desconocido: {evento}'}, status=400)

        return JsonResponse({'status': 'ok', 'mensaje': mensaje})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def sincronizar_usuario_desde_gh(data):
    """
    Crea o actualiza usuario desde datos de Gestión Humana (webhook).
    - Clave canónica: uuid_gh (data['uuid']), fallback a gestion_humana_id.
    - Escribe SOLO cuando el valor realmente cambió (update_fields).
    - La desactivación de GH se propaga (True→False), pero GH nunca
    reactiva un usuario que Inventario desactivó localmente.
    """

    from django.db.models import Q
    from .models import PerfilUsuario

    uuid_gh = data["uuid"]
    gh_id = data['id']

    perfil = (
        PerfilUsuario.objects.select_related("user")
        .filter(Q(uuid_gh=uuid_gh) | Q(gestion_humana_id=gh_id))
        .first()
    )

    if perfil:
        usuario = perfil.user
        accion = "actualizado"
        if not perfil.uuid_gh:
            perfil.uuid_gh = uuid_gh
            perfil.save(update_fields=['uuid_gh'])

    else:
        username = data.get("username", f"user_{gh_id}")
        usuario = User.objects.create_user(
            username=username,
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
        )
        usuario.set_unusable_password()
        usuario.save()

        perfil = PerfilUsuario.objects.create(
            user=usuario,
            gestion_humana_id=gh_id,
            uuid_gh=uuid_gh
        )
        accion = 'creado'

    cambios = []

    if usuario.first_name != data.get('first_name', ''):
        usuario.first_name = data.get('first_name', '')
        cambios.append('first_name')

    if usuario.last_name != data.get('last_name', ''):
        usuario.last_name = data.get('last_name', '')
        cambios.append('last_name')

    if usuario.email != data.get('email', ''):
        usuario.email = data.get('email', '')
        cambios.append('email')

    if not bool(data.get("is_active", True)) and usuario.is_active:
        usuario.is_active = False
        cambios.append('is_active')

    if cambios:
        usuario.save(update_fields=cambios)

    if data.get('cargo_contrato') is not None and perfil.cargo_contrato != data.get("cargo_contrato"):
        perfil.cargo_contrato = data.get('cargo_contrato')
        perfil.save(update_fields=['cargo_contrato'])

    return f"Usuario {usuario.username} - {accion}"


def desactivar_usuario_gh(gh_id):
    """Desactiva usuario cuando se elimina en GH"""
    from .models import PerfilUsuario

    try:
        perfil = PerfilUsuario.objects.select_related('user').get(
            gestion_humana_id=gh_id
        )
        usuario = perfil.user
        usuario.is_active = False
        usuario.save()

        return f"Usuario {usuario.username} desactivado"

    except PerfilUsuario.DoesNotExist:
        return f"Usuario GH#{gh_id} no encontrado"


def cerrar_sesiones_usuario_gh(gh_id):
    """Cierra sesiones cuando cambia contraseña en GH"""
    from .models import PerfilUsuario
    from django.contrib.sessions.models import Session

    try:
        perfil = PerfilUsuario.objects.select_related('user').get(
            gestion_humana_id=gh_id
        )
        usuario = perfil.user

        # Eliminar sesiones activas
        Session.objects.filter(
            session_data__contains=f'"_auth_user_id": "{usuario.id}"'
        ).delete()

        return f"Sesiones de {usuario.username} cerradas"

    except PerfilUsuario.DoesNotExist:
        return f"Usuario GH#{gh_id} no encontrado"



