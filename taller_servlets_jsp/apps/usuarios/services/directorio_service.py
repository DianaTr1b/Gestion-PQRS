import logging

import requests
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model

from apps.usuarios.models import PerfilUsuario

logger = logging.getLogger(__name__)

DIRECTORIO_CACHE_KEY = 'directorio_colaboradores_gh'
DIRECTORIO_TTL = 3600 * 12  # 12h
SYNC_GUARD_KEY = 'ultima_sync_directorio_gh'
SYNC_GUARD_TTL = 3600  # 1h

def _pull_usuarios_gh():
    """Descarga el catálogo de colaboradores activos desde Gestión Humana"""
    response = requests.post(
        f"{settings.GESTION_HUMANA_URL}/microservice/api-sync/pull/bulk/",
        headers={
            'X-Client-ID': settings.GESTION_HUMANA_CLIENT_ID,
            'X-Client-Secret': settings.GESTION_HUMANA_CLIENT_SECRET
        },
        json={'solo_activos': True},
        timeout=settings.GESTION_HUMANA_TIMEOUT
    )
    response.raise_for_status()
    return response.json().get('usuarios', [])

def obtener_directorio(forzar=False):
    """Cátalogo de colaboradores de RH para asignaciones (NO AUTH)"""
    datos = None if forzar else cache.get('DIRECTORIO_CACHE_KEY')
    if datos is None:
        datos = _pull_usuarios_gh()
        cache.set('DIRECTORIO_CACHE_KEY', datos, 'DIRECTORIO_TTL')
    return datos

def _sincronizar_usuario(user_data):
    """Crea o actualiza un colaborador local a partir de su dato de GH."""
    User = get_user_model()
    gh_id = user_data.get("id")
    uuid_gh = user_data.get("uuid")
    username = user_data.get("username") or f"user_{gh_id}"

    perfil = None
    if uuid_gh:
        perfil = PerfilUsuario.objects.select_related("user").filter(uuid_gh=uuid_gh).first()
    if perfil and not uuid_gh:
        perfil = PerfilUsuario.objects.select_related("user").filter(gestion_humana_id=gh_id).first()

    if perfil:
        usuario = perfil.user
        creado = False

    else:
        creado = True
        usuario, _ = User.objects.get_or_create(
            username=username,
            defaults={
                'email': user_data.get("email", ""),
                'first_name': user_data.get("first_name", ""),
                'last_name': user_data.get("last_name", "")
            },
        )
        if not usuario.has_usable_password():
            usuario.set_unusable_password()
            usuario.save(update_fields=['password'])
        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=usuario,
            defaults={
                'gestion_humana_id': gh_id,
                'uuid_gh': uuid_gh
            }
        )

    cambios_user = []
    if usuario.first_name != user_data.get("first_name", ""):
        usuario.first_name = user_data.get("first_name", "")
        cambios_user.append("first_name")
    if usuario.last_name != user_data.get("last_name", ""):
        usuario.last_name = user_data.get("last_name", "")
        cambios_user.append("last_name")
    if usuario.email != user_data.get("email", ""):
        usuario.email = user_data.get("email", "")
        cambios_user.append("email")
    if not bool(user_data.get("is_active", True)) and usuario.is_active:
        usuario.is_active = False
        cambios_user.append("is_active")
    if cambios_user:
        usuario.save(update_fields=cambios_user)

    cambios_perfil = []
    if perfil.uuid_gh != uuid_gh:
        perfil.uuid_gh = uuid_gh
        cambios_perfil.append("uuid_gh")
    cargo = user_data.get("cargo_contrato", "")
    if perfil.cargo_contrato != cargo:
        perfil.cargo_contrato = cargo
        cambios_perfil.append("cargo_contrato")
    perfil.ultima_sincronizacion_gh = timezone.now()
    cambios_perfil.append('ultima_sincronizacion_gh')
    if cambios_perfil:
        perfil.save(update_fields=cambios_perfil)

    return perfil, creado

def sincronizar_directorio(forzar=False):
    """
    Trae el directorio de GH y crea/actualiza los perfiles locales.

    Con guardar cache (1h) para no golpear a Talento en cada request.
    Tolerante a fallos: si Talento no responde, loguea y continua con datos locales.
    """
    if not forzar and cache.get("SYNC_GUARD_KEY"):
        return 0,0

    try:
        usuarios = _pull_usuarios_gh()
    except Exception as e:
        logger.error('Sync Talento falló: %s', e)
        return 0,0

    creados = actualizados = 0
    for user_data in usuarios:
        _, creado = _sincronizar_usuario(user_data)
        if creado:
            creados += 1
        else:
            actualizados += 1

    cache.set(DIRECTORIO_CACHE_KEY, usuarios, DIRECTORIO_TTL)
    cache.set(SYNC_GUARD_KEY, True, SYNC_GUARD_TTL)
    return creados, actualizados
