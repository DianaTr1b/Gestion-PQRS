from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Rol, PerfilUsuario

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'total_usuarios']
    search_fields = ['nombre']
    ordering = ['nombre']

    def total_usuarios(self, obj):
        return obj.usuarios.count()
    total_usuarios.short_description = 'Total usuarios'


# Inline para mostrar PerfilUsuario dentro del admin de User
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    fk_name = 'user'
    fields = ('rol', 'estado', 'puede_autorizar','accesos_software')
    filter_horizontal=('accesos_software',)


# Admin personalizado para User que incluye el perfil
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_rol', 'get_estado', 'get_puede_autorizar', 'is_active']
    list_filter = ['is_active', 'perfil__rol', 'perfil__estado', 'perfil__puede_autorizar']
    
    def get_rol(self, obj):
        return obj.perfil.rol.nombre if hasattr(obj, 'perfil') and obj.perfil.rol else '-'
    get_rol.short_description = 'Rol'
    get_rol.admin_order_field = 'perfil__rol'
    
    def get_estado(self, obj):
        if hasattr(obj, 'perfil'):
            color = 'green' if obj.perfil.estado == 'Activo' else 'red'
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
                color, obj.perfil.estado
            )
        return '-'
    get_estado.short_description = 'Estado'
    
    def get_puede_autorizar(self, obj):
        if hasattr(obj, 'perfil'):
            if obj.perfil.puede_autorizar:
                return format_html(
                    '<span style="color: green;"><i class="bi bi-check-circle-fill"></i> Sí</span>'
                )
            else:
                return format_html(
                    '<span style="color: gray;">No</span>'
                )
        return '-'
    get_puede_autorizar.short_description = 'Puede Autorizar'
    get_puede_autorizar.admin_order_field = 'perfil__puede_autorizar'


# Desregistrar el admin por defecto de User y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Admin separado para PerfilUsuario (opcional, para gestión directa)
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    # SOLUCIÓN: Usamos get_full_name en lugar del campo 'nombre' que causaba el error
    list_display = ['get_username', 'get_full_name', 'cargo_contrato' ,'rol', 'estado', 'puede_autorizar']
    list_filter = ['rol', 'estado', 'puede_autorizar']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    list_editable = ['puede_autorizar']

    filter_horizontal = ('accesos_software',)
    
    fieldsets = (
        ('Usuario Relacionado', {
            'fields': ('user',)
        }),
        ('Información del Perfil', {
            # SOLUCIÓN: Solo los campos reales del Perfil
            'fields': ('rol', 'estado', 'puede_autorizar', 'accesos_software', 'cargo_contrato')
        }),
    )
    
    def get_username(self, obj):
        return obj.user.username if obj.user else '-'
    get_username.short_description = 'Usuario'
    get_username.admin_order_field = 'user__username'

    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else '-'
    get_full_name.short_description = 'Nombre Completo'