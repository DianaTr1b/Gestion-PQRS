from django.core.management.base import BaseCommand, CommandError
from apps.usuarios.models import PerfilUsuario


class Command(BaseCommand):
    help = (
        "Asigna/Revoca is_staff e is_superuser a un usuario LOCAL de Inventario "
        "(independiente de los roles de Gestión Humana)" 
    )

    def add_arguments(self, parser):
        parser.add_argument('--username', help='Username del usuario local')
        parser.add_argument('--uuid', dest='uuid_gh', help='UUID (sub) en Gestión Humana')
        parser.add_argument('--gh-id', dest='gh_id', type=int, help='ID numérico en Gestión Humana')
        parser.add_argument('--unset', action='store_true', help='Quitar el rol de superusuario')

    def handle(self, *args, **options):
        username = options.get('username')
        uuid_gh = options.get('uuid_gh')
        gh_id = options.get('gh_id')

        if not any([username, uuid_gh, gh_id]):
            raise CommandError('Indica al menos uno de: --username, --uuid o --gh-id')

        perfil = None
        if username:
            perfil = PerfilUsuario.objects.select_related('user').filter(user__username=username).first()
        if perfil is None and uuid_gh:
            perfil = PerfilUsuario.objects.select_related('user').filter(uuid_gh=uuid_gh).first()
        if perfil is None and gh_id:
            perfil = PerfilUsuario.objects.select_related('user').filter(gestion_humana_id=gh_id).first()

        if perfil is None:
            raise CommandError('No se encontró ningún usuario local con esos criterios.')

        user = perfil.user

        if options.get("unset"):
            user.is_staff = False
            user.is_superuser = False
            user.save(update_fields=['is_staff', 'is_superuser'])
            self.stdout.write(self.style.WARNING(f'Rol de superusuario removido a {user.username}.'))

        else:
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=['is_staff', 'is_superuser'])
            self.stdout.write(self.style.SUCCESS(
                f'{user.username} es ahora superusuario de Inventario.'
            ))

# python manage.py asignar_superusuario --username <cedula_talento>

