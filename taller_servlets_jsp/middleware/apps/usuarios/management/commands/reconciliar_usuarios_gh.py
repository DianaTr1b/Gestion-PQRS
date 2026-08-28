import requests

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count, Q


class Command(BaseCommand):
    help = (
        'Backfill de uuid_gh desde Gestión Humana y fusión de PerfilUsuario '
        'duplicados (misma identidad GH). Corre primero con --dry-run.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Solo reporta qué se haría, sin modificar nada.')

    def handle(self, *args, **options):
        dry = options['dry_run']
        from apps.usuarios.models import PerfilUsuario

        mapa = self._mapa_id_uuid()

        # 1) Backfill de uuid_gh en perfiles creados por webhook/pull
        pendientes = PerfilUsuario.objects.filter(
            uuid_gh__isnull=True,
            gestion_humana_id__isnull=False,
        )
        for perfil in pendientes:
            nuevo = mapa.get(perfil.gestion_humana_id)
            if not nuevo:
                continue
            self._linea(dry, f"[backfill] perfil {perfil.id} ({perfil.user.username}) uuid={nuevo}")
            if not dry:
                PerfilUsuario.objects.filter(pk=perfil.pk).update(uuid_gh=nuevo)

        # 2) Fusión de duplicados (mismo uuid_gh)
        grupos = (
            PerfilUsuario.objects
            .values('uuid_gh')
            .annotate(total=Count('id'))
            .filter(total__gt=1, uuid_gh__isnull=False)
        )
        for g in grupos:
            miembros = list(
                PerfilUsuario.objects.filter(uuid_gh=g['uuid_gh']).select_related('user')
            )
            self._fusionar(miembros, dry)

    def _mapa_id_uuid(self):
        try:
            resp = requests.post(
                f"{settings.GESTION_HUMANA_URL}/microservice/api-sync/pull/bulk/",
                headers={
                    'X-Client-ID': settings.GESTION_HUMANA_CLIENT_ID,
                    'X-Client-Secret': settings.GESTION_HUMANA_CLIENT_SECRET,
                },
                json={'solo_activos': False},
                timeout=settings.GESTION_HUMANA_TIMEOUT,
            )
            resp.raise_for_status()
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'Error consultando GH: {exc}'))
            return {}
        return {u.get('id'): u.get('uuid') for u in resp.json().get('usuarios', [])}

    def _referencias(self, perfil):
        from apps.inventario.models import Elemento, DetalleMovimiento, MovimientoInventario
        n = Elemento.objects.filter(usuario_actual=perfil).count()
        n += Elemento.objects.filter(usuario_registro=perfil).count()
        n += Elemento.objects.filter(bodega_actual=perfil).count()
        n += DetalleMovimiento.objects.filter(usuario_actual=perfil).count()
        n += MovimientoInventario.objects.filter(
            Q(usuario_origen=perfil) | Q(usuario_destino=perfil)
            | Q(usuario_registro=perfil) | Q(usuario_autoriza=perfil)
        ).count()
        return n

    def _fusionar(self, miembros, dry):
        from apps.inventario.models import Elemento, DetalleMovimiento, MovimientoInventario
        from apps.mantenimiento.models import Mantenimiento

        # Canónico: prefiere staff/superuser, luego más referencias, luego id menor.
        canon = max(
            miembros,
            key=lambda p: (
                p.user.is_staff or p.user.is_superuser,
                self._referencias(p),
                -p.id,
            ),
        )

        for dup in miembros:
            if dup.pk == canon.pk:
                continue
            self._linea(
                dry,
                f"[duplicado] {dup.user.username} (perfil {dup.id}) "
                f"-> canonico {canon.user.username} (perfil {canon.id})",
            )
            if dry:
                continue

            # Reapuntar referencias a PerfilUsuario
            Elemento.objects.filter(usuario_actual=dup).update(usuario_actual=canon)
            Elemento.objects.filter(usuario_registro=dup).update(usuario_registro=canon)
            Elemento.objects.filter(bodega_actual=dup).update(bodega_actual=canon)
            DetalleMovimiento.objects.filter(usuario_actual=dup).update(usuario_actual=canon)
            MovimientoInventario.objects.filter(usuario_origen=dup).update(usuario_origen=canon)
            MovimientoInventario.objects.filter(usuario_destino=dup).update(usuario_destino=canon)
            MovimientoInventario.objects.filter(usuario_registro=dup).update(usuario_registro=canon)
            MovimientoInventario.objects.filter(usuario_autoriza=dup).update(usuario_autoriza=canon)

            # Reapuntar referencias a auth_user (Mantenimiento.tecnico)
            Mantenimiento.objects.filter(tecnico=dup.user).update(tecnico=canon.user)

            # Fusionar accesos_software
            for sw in dup.accesos_software.all():
                canon.accesos_software.add(sw)

            # Eliminar el duplicado (borra el perfil por CASCADE)
            dup.user.delete()

    def _linea(self, dry, texto):
        estilo = self.style.WARNING if dry else self.style.SUCCESS
        self.stdout.write(estilo(('[dry-run] ' if dry else '') + texto))