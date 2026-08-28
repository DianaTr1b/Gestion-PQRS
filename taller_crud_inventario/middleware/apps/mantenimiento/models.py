from django.db import models
from django.contrib.auth.models import User
from apps.inventario.models import Elemento


class Mantenimiento(models.Model):
    TIPO_MANTENIMIENTO_CHOICES = [
        ('Preventivo', 'Preventivo'),
        ('Correctivo', 'Correctivo'),
        ('Actualizacion', 'Actualización'),
    ]

    elemento = models.ForeignKey(
        Elemento,
        on_delete=models.PROTECT,
        related_name='mantenimientos',
        verbose_name="Elemento"
    )
    tecnico = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='mantenimientos_realizados',
        verbose_name="Técnico Responsable"
    )
    fecha_ejecucion = models.DateField(verbose_name="Fecha de Ejecución")
    tipo_mantenimiento = models.CharField(
        max_length=20,
        choices=TIPO_MANTENIMIENTO_CHOICES,
        verbose_name="Tipo de Mantenimiento"
    )
    seguimiento_claves = models.TextField(
        blank=True,
        null=True,
        verbose_name="Seguimiento de Claves"
    )
    informe_equipo = models.TextField(
        blank=True,
        null=True,  
        verbose_name="Informe del Equipo"
    )
    informe_usuario = models.TextField(
        blank=True,
        null=True,
        verbose_name="Informe del Usuario"
    )
    informe_fecha = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha del Informe"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )

    class Meta:
        db_table = 'mantenimientos'
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'
        ordering = ['-fecha_ejecucion']

    def __str__(self):
        return f"{self.tipo_mantenimiento} - {self.elemento.nombre} ({self.fecha_ejecucion})"