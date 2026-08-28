from django.contrib import admin
from django.utils.html import format_html
from .models import Mantenimiento

@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'elemento', 'tipo_mantenimiento',
        'tecnico', 
        'fecha_ejecucion',
    ]
    list_filter = [
        'tipo_mantenimiento',
        'fecha_ejecucion', 'tecnico'
    ]
    search_fields = [
        'elemento__nombre', 'elemento__serial','observaciones'
    ]
    ordering = ['-fecha_ejecucion']
    date_hierarchy = 'fecha_ejecucion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'elemento', 'tecnico', 
                'tipo_mantenimiento',
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_ejecucion', 'informe_fecha'
            )
        }),
        ('Detalles del Mantenimiento', {
            'fields': (
                'seguimiento_claves',
                'informe_equipo',
                'informe_usuario'
            )
        }),
        ('Observaciones Adicionales', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )