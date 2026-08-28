# Migration manual.
import uuid

from django.db import migrations, models


def rellenar_uuid_nulos(apps, schema_editor):
    """Rellena con un uuid temporal los perfiles huérfanos (sin dato en GH)."""
    PerfilUsuario = apps.get_model('usuarios', 'PerfilUsuario')
    for p in PerfilUsuario.objects.filter(uuid_gh__isnull=True):
        p.uuid_gh = uuid.uuid4()
        p.save(update_fields=['uuid_gh'])


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0008_perfilusuario_uuid_gh'),
    ]

    operations = [
        migrations.RunPython(rellenar_uuid_nulos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='perfilusuario',
            name='uuid_gh',
            field=models.UUIDField(
                db_index=True,
                help_text='Identidad inmutable (sub) del usuario en Gestión Humana (IdP)',
                unique=True,
            ),
        ),
    ]