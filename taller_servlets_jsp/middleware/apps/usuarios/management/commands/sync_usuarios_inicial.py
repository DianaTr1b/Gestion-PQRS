import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from apps.usuarios.services.directorio_service import sincronizar_directorio

class Command(BaseCommand):
    help = 'Sincronización inicial desde Gestión Humana'

    def handle(self, *args, **options):
        creados, actualizados = sincronizar_directorio(forzar=True)
        self.stdout.write(self.style.SUCCESS(
            f'✓ Creados: {creados} | Actualizados: {actualizados}'
        ))