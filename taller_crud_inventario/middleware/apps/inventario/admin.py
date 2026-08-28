from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from .models import Categoria, Elemento, MovimientoInventario, DetalleMovimiento, NombreElemento, PlataformaSoftware, Rol
from apps.usuarios.models import PerfilUsuario

# ==========================================
# GESTIÓN DE IDENTIDAD Y ACCESOS
# ==========================================
admin.site.register(PlataformaSoftware)

class RolAdmin(admin.ModelAdmin):
    filter_horizontal = ('accesos_por_defecto',) 

admin.site.register(Rol, RolAdmin)
class PerfilAdmin(admin.ModelAdmin):
    filter_horizontal = ('accesos_adicionales',)

# admin.site.register(Perfil, PerfilAdmin)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'estado', 'total_elementos']
    list_filter = ['estado']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    
    def total_elementos(self, obj):
        return obj.elementos.count()
    total_elementos.short_description = 'Total Elementos'


@admin.register(NombreElemento)
class NombreElementoAdmin(admin.ModelAdmin):
    list_display = [
        'id','categoria','nombre','activo',
        'requiere_serial','requiere_imei','requiere_imei2',
        'requiere_color','requiere_marca','requiere_modelo',
        'requiere_operador','requiere_numero','requiere_mac',
        'requiere_correo' # <-- NUEVO
        ]
    list_filter = [
        'categoria','activo',
        'requiere_serial','requiere_imei','requiere_imei2',
        'requiere_color', 'requiere_marca','requiere_modelo',
        'requiere_operador','requiere_numero', 'requiere_capacidad',
        'requiere_tipo','requiere_caracteristica', 'requiere_puertos',
        'requiere_mac', 'requiere_correo' # <-- NUEVO
        ]
    search_fields = ['nombre','categoria__nombre']
    list_editable = ['activo']

    fieldsets=(
        ('Información Básica', {
            'fields': ('categoria', 'activo')
        }),
        ('Identificación del Elemento / Software', {
            'fields':(
                'nombre', # <-- MOVIDO AQUÍ SEGÚN TU SOLICITUD
                'requiere_serial','requiere_imei',
                'requiere_imei2','requiere_mac'
            ),
            'description': 'Escribe el nombre del software o equipo, y marca sus identificadores únicos.'
        }),
        ('Caracteristicas Físicas', {
            'fields':(
                'requiere_color','requiere_marca','requiere_modelo',
                'requiere_capacidad', 'requiere_tipo', 'requiere_caracteristica'
            ),
            'description': 'Características físicas y técnicas del elemento'
        }),
        ('Comunicación, Conectividad y Acceso', {
            'fields': (
                'requiere_correo', # <-- NUEVO CAMPO AÑADIDO AQUÍ
                'requiere_operador','requiere_numero', 'requiere_puertos'
            ),
            'description': 'Campos para dispositivos de comunicación, red y acceso a plataformas de software'
        }),
    )


@admin.register(Elemento)
class ElementoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_nombre_elemento', 'condicion', 'usuario_actual_display',
        'cuenta_asociada', 'estado_badge', 'bodega_actual',
        'garantia_vigente'
    ]
    list_filter = [
        'condicion', 'periodicidad_pago', 'estado', 'categoria', 
        'bodega_actual__rol__nombre', 'marca', 'fecha_compra', 'fecha_registro'
    ]
    search_fields = [
        'id', 'nombre_elemento__nombre', 'marca', 'modelo', 'serial', 
        'imei', 'descripcion', 'cuenta_asociada'
    ]
    readonly_fields = ['fecha_registro', 'ultimo_movimiento']
    ordering = ['-fecha_registro']
    date_hierarchy = 'fecha_compra'
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'id', 'condicion', 'periodicidad_pago',
                'categoria', 'nombre_elemento', 'compania', 'descripcion'
            )
        }),
        ('Detalles Técnicos', {
            'fields': (
                'tipo_cuenta', 'cuenta_asociada', 'elemento_padre', 
                'marca', 'modelo', 'serial', 'imei', 'imei_2',
                'operador', 'numero', 'capacidad', 'tipo',
                'caracteristica', 'puertos', 'mac'
            ),
            'classes': ('collapse',)
        }),
        ('Ubicación y Asignación', {
            'fields': (
                'bodega_actual', 
                'usuario_registro', 'estado'
            )
        }),
        ('Información Financiera', {
            'fields': ('fecha_compra', 'garantia_hasta'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_registro', 'ultimo_movimiento'),
            'classes': ('collapse',)
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name in ['elemento', 'elemento_padre']:
            def custom_label(obj):
                cat = obj.categoria.nombre.lower() if obj.categoria else ""
                info = (obj.cuenta_asociada or "Sin correo") if ("software" in cat or "licencia" in cat) else f"{obj.marca} {obj.modelo}"
                return f"[{obj.id}] - {obj.nombre} ({info})"
            formfield.label_from_instance = custom_label
        return formfield

    def estado_badge(self, obj):
        colores = {
            'Disponible': '#28a745',
            'Asignado': '#007bff',
            'Mantenimiento': '#ffc107',
            'Baja': '#dc3545'
        }
        color = colores.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.estado
        )
    estado_badge.short_description = 'Estado'
    
    def usuario_actual_display(self, obj):
        if obj.usuario_actual:
            return format_html(
                '<span style="color: #007bff; font-weight: bold;">👤 {}</span>',
                obj.usuario_actual.nombre
            )
        return format_html(
            '<span style="color: #6c757d; font-style: italic;"> Sin asignar</span>'
        )
    usuario_actual_display.short_description = 'Usuario Actual'

 
    def garantia_vigente(self, obj):
        if obj.esta_en_garantia():
            return format_html(
                '<span style="color: green;">✓ Vigente</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Vencida</span>'
        )
    garantia_vigente.short_description = 'Garantía'
    
    actions = [
        'marcar_disponible', 'enviar_a_mantenimiento', 
        'dar_de_baja', 'liberar_elementos'
    ]
    
    def marcar_disponible(self, request, queryset):
        for elemento in queryset:
            elemento.liberar()
        self.message_user(request, f'{queryset.count()} elementos marcados como disponibles.')
    marcar_disponible.short_description = 'Marcar como Disponible'
    
    def enviar_a_mantenimiento(self, request, queryset):
        for elemento in queryset:
            elemento.enviar_mantenimiento()
        self.message_user(request, f'{queryset.count()} elementos enviados a mantenimiento.')
    enviar_a_mantenimiento.short_description = 'Enviar a Mantenimiento'
    
    def dar_de_baja(self, request, queryset):
        for elemento in queryset:
            elemento.dar_baja()
        self.message_user(request, f'{queryset.count()} elementos dados de baja.')
    dar_de_baja.short_description = 'Dar de Baja'
    
    def liberar_elementos(self, request, queryset):
        for elemento in queryset:
            if elemento.usuario_actual:
                elemento.liberar()
        self.message_user(request, 'Elementos liberados correctamente.')
    liberar_elementos.short_description = 'Liberar Asignación'

    def get_nombre_elemento(self, obj):
        """Muestra el nombre del elemento"""
        if obj.nombre_elemento:
            return obj.nombre_elemento.nombre
        return "-"
    get_nombre_elemento.short_description ='Elemento'
    get_nombre_elemento.admin_order_field = 'nombre_elemento__nombre'



# INLINE para DetalleMovimiento
class DetalleMovimientoInline(admin.TabularInline):
    model = DetalleMovimiento
    extra = 1
    fields = [
        'elemento', 'cantidad', 
        'estado_elemento_antes', 'estado_elemento_despues',
        'observaciones_elemento'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'elemento':
            def custom_label(obj):
                cat = obj.categoria.nombre.lower() if obj.categoria else ""
                info = (obj.cuenta_asociada or "Sin correo") if ("software" in cat or "licencia" in cat) else f"{obj.marca} {obj.modelo}"
                return f"[{obj.id}] - {obj.nombre} ({info})"
            formfield.label_from_instance = custom_label
        return formfield

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'elemento':
            kwargs["queryset"] = Elemento.objects.filter(estado='Disponible')
        formfield =super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'elemento':
            formfield.label_from_instance = lambda obj: f"ID :{obj.id} - {obj.nombre} ({obj.marca}{obj.modelo})"

        return formfield

class DetalleMovimientoInline(admin.TabularInline):
    model = DetalleMovimiento
    extra = 1
    fields = [
        'elemento', 'cantidad', 
        'estado_elemento_antes', 'estado_elemento_despues',
        'observaciones_elemento'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # 1. Filtramos primero para que solo salgan los Disponibles
        if db_field.name == 'elemento':
            kwargs["queryset"] = Elemento.objects.filter(estado='Disponible')
            
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

        # 2. Le damos el formato visual personalizado (Unificamos tus dos lógicas)
        if db_field.name == 'elemento':
            def custom_label(obj):
                cat = obj.categoria.nombre.lower() if obj.categoria else ""
                info = (obj.cuenta_asociada or "Sin correo") if ("software" in cat or "licencia" in cat) else f"{obj.marca} {obj.modelo}"
                return f"[{obj.id}] - {obj.nombre} ({info})"
                
            formfield.label_from_instance = custom_label
            
        return formfield
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tipo_movimiento_badge', 
        'usuario_registro', 'fecha_movimiento','hora_movimiento',
        'estado_movimiento_badge', 'total_elementos_mov'
    ]
    list_filter = [
        'tipo_movimiento', 'estado_movimiento',
        'fecha_movimiento', 'usuario_registro'
    ]
    search_fields = [
        'observaciones', 'usuario_destino__nombre',
        'usuario_origen__nombre','id'
    ]
    readonly_fields = ['fecha_movimiento','hora_movimiento']
    ordering = ['-fecha_movimiento']
    date_hierarchy = 'fecha_movimiento'
    inlines = [DetalleMovimientoInline]
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': (
                'tipo_movimiento','estado_movimiento', 
                'usuario_registro', 'fecha_movimiento', 'hora_movimiento'
            )
        }),
        ('Origen y Destino', {
            'fields': (
                'usuario_origen', 'usuario_destino',
            ),
            'description':'Importante: El Usuario Destino se aplicará automaticamente a todos los elementos de este movimiento.'
        }),
        
        ('Documentación', {
            'fields': ('observaciones', 'documento_soporte'),
            'classes': ('collapse',),
            'description': 'Observaciones generales del movimiento (se aplican a todos los elementos)'
        }),
    )
    
    def tipo_movimiento_badge(self, obj):
        colores = {
            'Asignacion': '#007bff',
            'Devolucion': '#28a745',
            'Traslado': '#17a2b8',
            'Entrada': '#6f42c1',
            'Baja': '#dc3545'
        }
        color = colores.get(obj.tipo_movimiento, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_tipo_movimiento_display()
        )
    tipo_movimiento_badge.short_description = 'Tipo'

    def estado_movimiento_badge(self, obj):
        colores = {
            'Pendiente': '#ffc107',
            'Realizado': '#28a745',
            'Cancelado': '#dc3545',
            'Anulado': '#343a40',
        }
        color = colores.get(obj.estado_movimiento, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_estado_movimiento_display()
        )
    estado_movimiento_badge.short_description = 'Estado Mov.'
    
    def total_elementos_mov(self, obj):
        total = obj.detalles.count()
        return format_html(
            '<strong style="color: #007bff;">{}</strong>', total
        )
    total_elementos_mov.short_description = 'Elementos'
    
    actions = ['marcar_realizado', 'cancelar_movimientos', 'anular_movimientos']
    
    def marcar_realizado(self, request, queryset):
        queryset.update(estado_movimiento='Realizado')
        self.message_user(request, f'{queryset.count()} movimientos marcados como realizados.')
    marcar_realizado.short_description = 'Marcar como Realizado'
    
    def cancelar_movimientos(self, request, queryset):
        queryset.update(estado_movimiento='Cancelado')
        self.message_user(request, f'{queryset.count()} movimientos cancelados.')
    cancelar_movimientos.short_description = 'Cancelar Movimientos'

    def anular_movimientos(self, request, queryset):
               
        # 1. Buscamos el "PerfilUsuario" del administrador que está haciendo la anulación
        try:
            admin_perfil = PerfilUsuario.objects.get(user=request.user)
        except:
            admin_perfil = None # Fallback por si el superusuario no tiene perfil creado
            
        movimientos_anulados = 0
        
        for movimiento in queryset:
            if movimiento.estado_movimiento != 'Anulado':
                
                # Forzamos el cambio del documento original a Anulado
                queryset.filter(id=movimiento.id).update(estado_movimiento='Anulado')
                
                # CREAMOS EL DOCUMENTO DE AUDITORÍA (Contra-movimiento automático)
                mov_reversion = MovimientoInventario.objects.create(
                    tipo_movimiento='Devolucion', 
                    estado_movimiento='Realizado',
                    # Usamos el perfil del admin, o si falla, usamos a quien registró el movimiento original
                    usuario_registro=admin_perfil if admin_perfil else movimiento.usuario_registro, 
                    usuario_origen=movimiento.usuario_destino, 
                    usuario_destino=movimiento.usuario_origen,
                    observaciones=f"REVERSIÓN AUTOMÁTICA: Este movimiento deshace los cambios del Folio anulado #{movimiento.id}.",
                    fecha_movimiento=timezone.now().date(),
                    hora_movimiento=timezone.now().time()
                )
                
                # Buscamos los equipos, los devolvemos y los registramos en el historial
                detalles = DetalleMovimiento.objects.filter(movimiento=movimiento)
                for detalle in detalles:
                    elemento = detalle.elemento
                    estado_anterior_al_retorno = elemento.estado
                    
                    if movimiento.usuario_origen:
                        elemento.usuario_actual = movimiento.usuario_origen
                        
                        rol_usuario = getattr(movimiento.usuario_origen, 'rol', None)
                        if rol_usuario and rol_usuario.nombre == 'Bodega':
                            elemento.estado = 'Disponible'
                        else:
                            elemento.estado = 'Asignado'
                            
                        elemento.save()
                    else:
                        elemento.liberar() 
                        
                    # VINCLAMOS EL EQUIPO AL NUEVO DOCUMENTO (Trazabilidad)
                    DetalleMovimiento.objects.create(
                        movimiento=mov_reversion,
                        elemento=elemento,
                        estado_elemento_antes=estado_anterior_al_retorno,
                        estado_elemento_despues=elemento.estado,
                        observaciones_elemento=f"Regresa a su estado original por anulación del Folio #{movimiento.id}."
                    )
                
                movimientos_anulados += 1
                
        if movimientos_anulados > 0:
            self.message_user(
                request, 
                f"Éxito: Se anularon {movimientos_anulados} movimientos y se generaron sus contra-movimientos para trazabilidad.", 
                messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                "⚠️ No se realizó ningún cambio.", 
                messages.WARNING
            )
    anular_movimientos.short_description = 'Anular movimientos (y generar reversión)'

    def save_related(self, request, form, formsets, change):
        movimiento = form.instance

        for formset in formsets:
            if formset.model == DetalleMovimiento:
                detalles_count = sum(1 for f in formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False))

                if detalles_count > 0 and movimiento.tipo_movimiento in ['Asignacion', 'Reasignacion']:
                    if not movimiento.usuario_destino:
                        from django.contrib import messages
                        messages.error(
                            request,
                            'ERROR: Debe seleccionar un Usuario Destino para movimientos de  tipo Asignación o Reasignación'
                            )
                        return
                    
        super().save_related(request, form, formsets, change)

    def save_model(self, request, obj, form, change):
        tipo = form.cleaned_data.get('tipo_movimiento')

        if tipo in ['Devolucion', 'Reasignacion']:
            if not form.cleaned_data.get('usuario_origen'):
                from django.contrib import messages
                messages.error(
                    request,
                    f'ERROR: El movimiento de tipo "{obj.get_tipo_movimiento_display()}"'
                    ' requiere seleccionar un "Usuario Origen".'
                )
                return
            
        if tipo in ['Asignacion', 'Reasignacion']:
            if not form.cleaned_data.get('usuario_destino'):
                from django.contrib import messages
                messages.error(
                    request,
                    f'ERROR: El movimiento de tipo "{obj.get_tipo_movimiento_display()}"'
                    ' requiere seleccionar un "Usuario Destino".'
                )
                return
        super().save_model(request, obj, form, change)
                

    class Media:
        js = ('inventario/js/movimiento_admin.js',)


@admin.register(DetalleMovimiento)
class DetalleMovimientoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'movimiento', 'elemento', 'cantidad',
        'estado_elemento_antes', 'estado_elemento_despues', 'usuario_actual'
    ]
    list_filter = [
        'estado_elemento_antes', 'estado_elemento_despues',
        'movimiento__tipo_movimiento', 'movimiento__fecha_movimiento'
    ]
    search_fields = [
            'elemento__nombre', 'elemento__serial',
        'movimiento__id', 'observaciones_elemento'
    ]
    readonly_fields = ['movimiento', 'elemento']
    ordering = ['-movimiento__fecha_movimiento']
    
    def estado_antes_badge(self, obj):
        colores = {
            'Óptimo': '#28a745',      
            'Regular': '#ffc107',
            'Deficiente': '#dc3545'
        }
        color = colores.get(obj.estado_elemento_antes, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.estado_elemento_antes or 'N/A'
        )
    estado_antes_badge.short_description = 'Estado Antes'

    def estado_despues_badge(self, obj):
        colores = {
            'Óptimo': '#28a745',
            'Regular': '#ffc107',
            'Deficiente': '#dc3545'
        }
        color = colores.get(obj.estado_elemento_despues, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.estado_elemento_despues or 'N/A'
        )
    estado_despues_badge.short_description = 'Estado Después'