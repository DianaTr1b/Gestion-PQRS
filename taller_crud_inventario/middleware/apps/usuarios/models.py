from django.db import models
from django.contrib.auth.models import User
from apps.inventario.choices import Ubicacion
from apps.inventario.choices import Ubicacion, EstadoChoices

class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Rol")
    permisos = models.TextField(verbose_name="Permisos", help_text="Descripción de permisos del rol")

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre}"
    

class PerfilUsuario(models.Model):
    """Extensión del modelo de User para crear campos personalizados"""
    TIPO_CHOICES =[
        ('usuario_final', 'Usuario Final'),
        ('tecnico', 'Técnico'),
        ('bodega','Bodega')
    ]
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='usuario_final',
        verbose_name="Tipo de Usuario"
    )
        
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )

    rol = models.ForeignKey(
        Rol, 
        on_delete=models.PROTECT, 
        related_name='usuarios',
        verbose_name="Rol",
        null=True
    )

    cargo_contrato = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Cargo del contrato'
    )

    ciudad = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices= Ubicacion.choices,
        verbose_name="Ciudad")

    estado = models.CharField(
        max_length=20,
        choices = EstadoChoices.choices,
        default = EstadoChoices.ACTIVO,
        verbose_name="Estado"
    )

    puede_autorizar = models.BooleanField(
        default=False,
        verbose_name="Puede Autorizar Movimientos",
        help_text="Marca si este usuario puede autorizar movimientos de inentario"
    )

    gestion_humana_id = models.IntegerField(
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text='ID del usuario en Gestión Humana (sistema maestro)'
    )

    uuid_gh = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        help_text='Identidad inmutable (sub) del usuario en Gestión Humana (IdP)',
    )

    ultima_sincronizacion_gh = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Última sincronización con Gestión Humana'
    )

    accesos_software = models.ManyToManyField(
        'inventario.PlataformaSoftware', 
        blank=True, 
        verbose_name="Software Asignado"
    )

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-id']

    def __str__(self):
        return f"{self.user.first_name} ({self.user.last_name})"
    
    @property
    def nombre(self):
        """Alias para mantener compatibilidad con código existente"""
        return self.user.get_full_name() or self.user.username
    
    @property
    def email(self):
        """Alias para mantener compatibilidad"""
        return self.user.email