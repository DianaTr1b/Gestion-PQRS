from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
from .choices import EstadoChoices, EstadoEquipo
from django.contrib.auth.models import User
from apps.usuarios.models import PerfilUsuario as Usuario
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# ==========================================
# GESTIÓN DE IDENTIDAD Y ACCESOS
# ==========================================
# 1. El catálogo base: no depende de nadie, debe ir primero.
class PlataformaSoftware(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Plataforma de Software"
        verbose_name_plural = "Plataformas de Software"

    def __str__(self):
        return self.nombre

# 2. Los roles: dependen de PlataformaSoftware, va después.
class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    accesos_por_defecto = models.ManyToManyField(PlataformaSoftware, blank=True)

    def __str__(self):
        return self.nombre

# # 3. El perfil: depende de Rol y de PlataformaSoftware, va al final.
# class Perfil(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_inventario')
#     rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
#     accesos_adicionales = models.ManyToManyField(PlataformaSoftware, blank=True)

#     def __str__(self):
#         return self.user.username

#======================================================================

def validar_peso_archivo(archivo):
    """Verifica que el archivo no supere los 2MB."""
    limite_mb = 2
    if archivo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"El archivo es demasiado grande. El tamaño máximo permitido es {limite_mb}MB.")

def ruta_documento_soporte(instance, filename):
    """
    Ruta para PDFs completados: firmas_movimientos/usuario/{username}/documentos/{archivo}.pdf
    """
    # Buscamos el usuario destino (quien recibe a final de cuentas el inventario)
    usuario = instance.usuario_destino or instance.usuario_registro
    
    if usuario and hasattr(usuario, 'user'):
        identificador = usuario.user.username
    else:
        identificador = getattr(usuario, 'username', 'sin_identificador')
        
    return f"firmas_movimientos/usuario/{identificador}/documentos/{filename}"

def ruta_firmas(instance, filename):
    """
    Ruta para imágenes de firmas: firmas_movimientos/usuario/{username}/firma/{archivo}.png
    """
    # Para la firma física, usamos el usuario que está firmando o registrando
    usuario = instance.usuario_destino or instance.usuario_registro
    
    if usuario and hasattr(usuario, 'user'):
        identificador = usuario.user.username
    else:
        identificador = getattr(usuario, 'username', 'sin_identificador')
        
    return f"firmas_movimientos/usuario/{identificador}/firma/{filename}"

class Categoria(models.Model):
    
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    estado = models.CharField(
        max_length=30, 
        choices=EstadoChoices.choices, 
        default='Activo',
        verbose_name="Estado"
    )

    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre}"

class NombreElemento(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='nombres_elementos',
        verbose_name='Categoría'
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Elemento'
    )
    requiere_serial = models.BooleanField(
        default=True,
        verbose_name='Requiere serial',
        help_text='Marca si este elemento requiere número de serie'
    )
    requiere_imei = models.BooleanField(
        default=False,
        verbose_name='Requiere IMEI',
        help_text='Marca si este elemento requiere IMEI'
    )
    requiere_imei2 =models.BooleanField(
        default=False,
        verbose_name='Requiere IMEI 2',
        help_text='Marca si este elemento requiere IMEI secundario (ej: Celulares dual SIM)'
    )
    requiere_color = models.BooleanField(
        default=False,
        verbose_name ='Requiere Color',
        help_text='Marca si este elemento requiere especificar color'
    )
    requiere_marca = models.BooleanField(
        default=True,
        verbose_name ='Requiere Marca',
        help_text='Ej: Samsung, HP , Dell'
    )
    requiere_modelo = models.BooleanField(
        default=True,
        verbose_name ='Requiere Moelo',
        help_text='Ej: Galaxy s21, Probook 450'
    )
    requiere_operador = models.BooleanField(
        default=False,
        verbose_name ='Requiere Operador',
        help_text='Ej: Claro, Movistar (para celulares y SIM)'
    )
    requiere_numero = models.BooleanField(
        default=False,
        verbose_name ='Requiere Número',
        help_text='Número de linea telefonica Para celulares y SIM'
    )
    requiere_capacidad = models.BooleanField(
        default=False,
        verbose_name ='Requiere Capacidad',
        help_text='Ej: 5000Gb, 1TB, 2 tolenadas(almacenamiento o peso)'
    )
    requiere_tipo = models.BooleanField(
        default=False,
        verbose_name ='Requiere Tipo',
        help_text='Ej: inalambrico, De cocina, de oficina '
    )
    requiere_caracteristica = models.BooleanField(
        default=False,
        verbose_name ='Requiere Caracteristica',
        help_text='Caracteristica especial del elemento'
    )
    requiere_puertos = models.BooleanField(
        default=False,
        verbose_name ='Requiere puerto',
        help_text='Ej: USB-A, HDMI, RJ45 (Para Swiches, routers,etc)'
    )
    requiere_mac = models.BooleanField(
        default=False,
        verbose_name ='Requiere MAC',
        help_text='Descripción adicional del elemento'
    )

    activo = models.BooleanField(
        default =True,
        verbose_name='Activo'
    )
    requiere_correo = models.BooleanField(
        default=False,
        verbose_name='Requiere Correo Electrónico'
    )

    class Meta:
        db_table ='nombres_elementos'
        verbose_name = 'Nombre de Elemento'
        verbose_name_plural = 'Nombres de Elementos'
        unique_together = ['categoria', 'nombre']
        ordering = ['categoria','nombre']

    def __str__(self):
        return f"{self.categoria.nombre} - {self.nombre}"    

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('Asignacion', 'Asignación'),
        ('Reasignacion', 'Reasignación'),
        ('Devolucion', 'Devolución'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Baja', 'Baja'),
    ]
    ESTADO_MOVIMIENTO_CHOICES = [
        ('Pendiente','Pendiente'),
        ('Realizado','Realizado'),
        ('Cancelado','Cancelado'),
        ('Anulado','Anulado'),
    ]

    usuario_origen = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='movimientos_origen', verbose_name="Usuario Origen")
    usuario_destino = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='movimientos_destino', verbose_name="Usuario Destino")
    usuario_registro = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='movimientos_registrados', verbose_name="Usuario que Registra")
    usuario_autoriza = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True, related_name='movimientos_autorizados', verbose_name="Autorizado por", help_text="Usuario que autoriza el movimiento", limit_choices_to={'puede_autorizar': True})

    tipo_movimiento = models.CharField(max_length=30, choices=TIPO_MOVIMIENTO_CHOICES, verbose_name="Tipo de Movimiento")
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Movimiento")
    hora_movimiento = models.TimeField(auto_now_add=True, verbose_name= "Hora del movimiento")
    estado_movimiento = models.CharField(max_length=20, choices = ESTADO_MOVIMIENTO_CHOICES, default='Pendiente', verbose_name= "Estado del Movimiento")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones Generales")
    documento_soporte = models.FileField(
        upload_to=ruta_documento_soporte,  
        validators=[validar_peso_archivo], 
        blank=True, 
        null=True, 
        verbose_name="Documento Soporte"
    )
    
    firma_recibe = models.ImageField(upload_to=ruta_firmas, blank=True, null=True, verbose_name='Firma Recibe')
    firma_elabora = models.ImageField(upload_to=ruta_firmas, blank=True, null=True, verbose_name='Firma Elabora')
    firma_autoriza = models.ImageField(upload_to=ruta_firmas, blank=True, null=True, verbose_name='Firma Autoriza')

    
    # Campo de base de datos
    es_firmado_total = models.BooleanField(default=False, verbose_name='Firmado Completamente')

    class Meta:
        db_table = 'movimientos_inventario'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha_movimiento','-hora_movimiento']

    def __str__(self):
        return f"MOV-{self.id}|{self.get_tipo_movimiento_display()}|{self.fecha_movimiento}"
    
    def save(self, *args, **kwargs):
        # 1. Validamos que las firmas tengan realmente un archivo (.name)
        tiene_recibe = bool(self.firma_recibe and self.firma_recibe.name)
        tiene_elabora = bool(self.firma_elabora and self.firma_elabora.name)
        
        firmas_completas = tiene_recibe and tiene_elabora
        
        # 2. Si el movimiento requiere autorización, validamos esa tercera firma
        if self.usuario_autoriza:
            tiene_autoriza = bool(self.firma_autoriza and self.firma_autoriza.name)
            if not tiene_autoriza:
                firmas_completas = False
                
        # 3. Actualizamos el campo booleano
        self.es_firmado_total = firmas_completas
        
        # 4. Forzamos el estado automáticamente
        if firmas_completas:
            self.estado_movimiento = 'Realizado'
        elif self.estado_movimiento == 'Realizado' and not firmas_completas:
            # Por si en algún momento se borra una firma por error, que regrese a pendiente
            self.estado_movimiento = 'Pendiente'
            
        super().save(*args, **kwargs)
    
    @property
    def necesita_notificacion_firma(self):
        """
        Lógica para decidir si enviar correo.
        Retorna True si faltan firmas físicas (imágenes).
        """
        # Si no hay firma de quien recibe o de quien elabora
        if not self.firma_recibe or not self.firma_elabora:
            return True
        # Si requiere autorización y no hay firma de autoriza
        if self.usuario_autoriza and not self.firma_autoriza:
            return True
        return False

    def aplicar_movimiento_a_elementos(self):
        """Ejecuta los cambios físicos en los equipos SOLO cuando el acta es legal (firmada)."""
        from django.utils import timezone
        
        for detalle in self.detalles.all():
            elemento = detalle.elemento
            tipo = self.tipo_movimiento
            usuario_destino = self.usuario_destino

            if tipo == 'Asignacion' or tipo == 'Reasignacion':
                if usuario_destino and usuario_destino.rol and usuario_destino.rol.nombre == 'Bodega':
                    elemento.estado = 'Disponible'
                    elemento.usuario_actual = None
                    elemento.fecha_asignacion = None
                    elemento.bodega_actual = usuario_destino
                    detalle.usuario_actual = None
                else:
                    elemento.estado = 'Asignado'
                    elemento.usuario_actual = usuario_destino
                    elemento.fecha_asignacion = timezone.now()
                    detalle.usuario_actual = usuario_destino

            elif tipo == 'Devolucion':
                elemento.estado = 'Disponible'
                elemento.usuario_actual = None
                elemento.fecha_asignacion = None
                detalle.usuario_actual = None

            elif tipo == 'Mantenimiento':
                elemento.estado = 'Mantenimiento'
                elemento.usuario_actual = None
                elemento.fecha_asignacion = None
                detalle.usuario_actual = None
                if self.usuario_destino:
                    elemento.bodega_actual = self.usuario_destino    

            elif tipo == 'Baja':
                elemento.estado = 'Baja'
                elemento.usuario_actual = None
                detalle.usuario_actual = None
                if self.usuario_destino:
                    elemento.bodega_actual = self.usuario_destino

            elemento.save()
            detalle.save(update_fields=['usuario_actual'])


class DetalleMovimiento(models.Model):

    movimiento= models.ForeignKey(
        MovimientoInventario,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Movimiento'
    )

    elemento =models.ForeignKey(
        'Elemento',
        on_delete = models.PROTECT,
        related_name='detalles_movimiento',
        verbose_name='Elemento'
    )

    cantidad = models.PositiveIntegerField(
        default= 1,
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad'
    )

    estado_elemento_antes = models.CharField(
        max_length=20,
        blank=True, null= True,
        choices=EstadoEquipo.choices,
        verbose_name="Estado Antes"     
    )

    estado_elemento_despues = models.CharField(
        max_length=20,
        blank=True, null= True,
        choices=EstadoEquipo.choices,
        verbose_name="Estado Después"     
    )

    observaciones_elemento = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones del Elemento"
    )

    usuario_actual = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='elementos_asignados_detalle',
        verbose_name="Usuario Actual"   
    )

    class Meta:
        db_table = 'detalle_movimiento'
        verbose_name="Detalle de movimiento"
        verbose_name_plural ="Detalles de Movimiento"
        ordering=['movimiento','elemento']
        unique_together = [['movimiento','elemento']]

    def __str__(self):
        return f"{self.movimiento.id} - {self.elemento.nombre}"
    
    def save(self, *args, **kwargs):
        is_new =self.pk is None
        super().save(*args,**kwargs)

        if is_new:
            # self.elemento.estado = self.estado_elemento_despues
            self.elemento.ultimo_movimiento = self.movimiento
            # self.elemento.save(update_fields=['ultimo_movimiento'])
            tipo = self.movimiento.tipo_movimiento
            usuario_destino = self.movimiento.usuario_destino

            if tipo in ['Asignacion','Reasignacion']  and not usuario_destino:
                raise ValueError(
                    f"Error: El movimiento de tipo '{tipo}' requiere un Usuario Destino." 
                    "Por favor, especifique a quien se asignarán los elementos."
                )

            # if tipo == 'Asignacion':
            #     if usuario_destino and usuario_destino.rol and usuario_destino.rol.nombre == 'Bodega':
            #         self.elemento.estado = 'Disponible'
            #         self.elemento.usuario_actual = None
            #         self.elemento.fecha_asignacion = None
            #         self.usuario_actual = None
            #         self.elemento.bodega_actual = usuario_destino
            #     else:
            #         self.elemento.estado = 'Asignado'
            #         self.elemento.usuario_actual = usuario_destino
            #         self.elemento.fecha_asignacion = timezone.now()
            #         self.usuario_actual = usuario_destino

            # elif tipo == 'Reasignacion':
            #     if usuario_destino and usuario_destino.rol and usuario_destino.rol.nombre == 'Bodega':
            #         self.elemento.estado = 'Disponible'
            #         self.elemento.usuario_actual = None
            #         self.elemento.fecha_asignacion = None
            #         self.usuario_actual = None
            #         self.elemento.bodega_actual = usuario_destino
            #     else:
            #         self.elemento.estado = 'Asignado'
            #         self.elemento.usuario_actual = usuario_destino
            #         self.elemento.fecha_asignacion = timezone.now()
            #         self.usuario_actual = usuario_destino

            # elif tipo == 'Devolucion':
            #     self.elemento.estado= 'Disponible'
            #     self.elemento.usuario_actual =None
            #     self.elemento.fecha_asignacion = None
            #     self.usuario_actual = None

            # elif tipo == 'Mantenimiento':
            #     self.elemento.estado = 'Mantenimiento'
            #     self.elemento.usuario_actual = None
            #     self.elemento.fecha_asignacion = None
            #     self.usuario_actual = None
            #     if self.movimiento.usuario_destino:
            #         self.elemento.bodega_actual = self.movimiento.usuario_destino    

            # elif tipo == 'Baja':
            #     self.elemento.estado ='Baja'
            #     self.elemento.usuario_actual =None
            #     self.usuario_actual = None
            #     if self.movimiento.usuario_destino:
            #         self.elemento.bodega_actual = self.movimiento.usuario_destino

            # self.elemento.save()

            # if tipo in ['Asignacion','Reasignacion','Devolucion','Baja']:
            #     super().save(update_fields=['usuario_actual'])

class Elemento(models.Model):

    ESTADO_CHOICES =[
        ('Disponible','Disponible'),
        ('Asignado','Asignado'),
        ('Mantenimiento','Mantenimiento'),
        ('Baja','Baja'),
    ]

    TIPO_CUENTA_CHOICES = [
        ('Principal','Principal'),
        ('Subcuenta','Subcuenta'),
    ]

    fecha_asignacion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Asignación"
    )

    id= models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name="ID del Elemento",
        help_text="Identificador único del elemento en el inventario()"
    )
    categoria= models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='elementos',
        verbose_name="categoria"
    )
    nombre_elemento = models.ForeignKey(
    NombreElemento,
    on_delete=models.PROTECT,
    related_name='elementos_relacionados',
    verbose_name='Nombre del Elemento'
    )
    bodega_actual = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='elementos_en_bodega',
        verbose_name='Bodega Actual',
        limit_choices_to={'rol__nombre':'Bodega'},
        help_text='Usuario con rol de bodega donde se encuentra actualmente el elemento'
    )
   
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='elementos_registrados',
        verbose_name="Usuario que registro"
    )
    COMPANIA_CHOICES = [
        ('ECL','ECL'),
        ('INTERCARGO','Intercargo'),
        ('ECOLOGISTICS','Ecologistics'),
        ('TLC','TLC'),
        ('TLSS','TLSS'),
    ]
    compania = models.CharField(
        max_length=20,
        choices=COMPANIA_CHOICES,
        default='ECL',
        verbose_name="Compañía"
    )

    usuario_actual = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='elementos_asignados',
        verbose_name='Usuario Actual'
        )
    
    ultimo_movimiento = models.ForeignKey(
        MovimientoInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='elementos_ultimo_mov',
        verbose_name='Último Movimiento'
    )    
    marca = models.CharField(
        max_length=100, 
        verbose_name="Marca"
    )
    modelo = models.CharField(
        max_length=100, 
        verbose_name="Modelo"
    )
    serial = models.CharField(
        max_length=100, 
        blank=True, null=True, 
        verbose_name="Serial"
    )
    imei = models.CharField(
        max_length=50, 
        blank=True, null=True, 
        verbose_name="IMEI"
    )
    imei_2=models.CharField(
        max_length=50, 
        blank=True,null=True, 
        verbose_name="IMEI 2"
    )
    color = models.CharField(
        max_length=50,
        blank=True , null=True,
        verbose_name='Color',
    )
    operador = models.CharField(
        max_length=50,
        blank=True , null=True,
        verbose_name='Operador',
        help_text='Ej:Claro, Movistar'
    )
    numero = models.CharField(
        max_length=20,
        blank=True , null=True,
        verbose_name='Número',
        help_text='Ej:Claro, Movistar'
    )
    capacidad = models.CharField(
        max_length=50,
        blank=True , null=True,
        verbose_name='Capacidad',
        help_text='Ej:500GB, 1TB, 2 toneladas'
    )
    tipo = models.CharField(
        max_length=50,
        blank=True , null=True,
        verbose_name='Tipo',
        help_text='Ej:SSD, HDD, Inalámbrico'
    )
    caracteristica = models.CharField(
        max_length=200,
        blank=True , null=True,
        verbose_name='Caracteristica',
        help_text='Ej:Caracteristica especial del elemento'
    )
    puertos = models.CharField(
        max_length=200,
        blank=True , null=True,
        verbose_name='Puertos',
        help_text='Ej:2xUSB-A, 1xHDMI, 4xRJ45'
    )
    mac = models.CharField(
        max_length=17,
        blank=True , null=True,
        verbose_name='Dirección MAC',
        help_text='Formato 12 digitos xx.xx.xx.xx.xx.xx'
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    factura = models.FileField(
        upload_to='documentos_elementos/facturas/',
        blank=True,
        null=True,
        verbose_name="Factura"
    )
    documento_adicional = models.FileField(
        upload_to='documentos_elementos/adicionales/',
        blank=True,
        null=True,
        verbose_name="Documento Adicional"
    )    
    estado = models.CharField(
        max_length=20,
        blank=True, null= True,
        choices=ESTADO_CHOICES,
        default='Disponible',
        verbose_name="Estado"
    )
    CONDICION_CHOICES = [
        ('Propio', 'Propio'),
        ('Rentado', 'En Renta'),
        ('Suscripcion','Suscripcion / Software'),
    ]
    
    PERIODICIDAD_CHOICES = [
        ('N/A', 'No Aplica'),
        ('Mensual', 'Mensual'),
        ('Bimestral', 'Bimestral'),
        ('Anual', 'Anual'),
    ]

    condicion = models.CharField(
        max_length=20, 
        choices=CONDICION_CHOICES, 
        default='Propio', 
        verbose_name='Condición del Equipo'
    )
    periodicidad_pago = models.CharField(
        max_length=20, 
        choices=PERIODICIDAD_CHOICES, 
        default='N/A', 
        verbose_name='Periodicidad de Pago',
        blank=True, null=True
    )

    tipo_cuenta=models.CharField(
        max_length=20,
        choices=TIPO_CUENTA_CHOICES,
        blank = True, null=True,
        verbose_name='Tipo de Cuenta'
    )

    elemento_padre=models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_elementos',
        verbose_name='Cuenta principal (Máster)',
        help_text='Seleccione el software Máster si esta es una sub-licencia o usuario'
    )
    
    cuenta_asociada = models.CharField(
        max_length=150,
        blank=True, 
        null=True,
        verbose_name='Cuenta / Correo Asociado',
        help_text ='Correo electrónico o usuario con el que se ingresa al software'
    )

    fecha_compra = models.DateField(verbose_name="Fecha de Compra")
    garantia_hasta = models.DateField(verbose_name="Garantía Hasta")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    @property
    def nombre(self):
        if hasattr(self,'nombre_elemento') and self.nombre_elemento:
            return self.nombre_elemento.nombre
        return "Sin nombre"
    
    class Meta:
        db_table = 'elementos'
        verbose_name = 'Elemento'
        verbose_name_plural = 'Elementos'
        ordering = ['-fecha_registro']

    def __str__(self):
        # 1. Validación blindada: Revisa la condición O el nombre de la categoría
        cat_nombre = self.categoria.nombre.lower() if self.categoria else ""
        
        if 'suscripcion' in str(self.condicion).lower() or 'software' in cat_nombre or 'licencia' in cat_nombre:
            identificador = self.cuenta_asociada if self.cuenta_asociada else "Sin correo asociado"
        else:
            identificador = f"{self.marca} {self.modelo}".strip()
            if not identificador or identificador == "None None":
                identificador = "Sin detalles técnicos"
        
        nombre = self.nombre_elemento.nombre if self.nombre_elemento else "Elemento"
        return f"[{self.id}] {nombre} - {identificador} ({self.estado})"

    def esta_en_garantia(self):
        """Verifica si el elemento está en garantía"""
        return date.today() <= self.garantia_hasta
    
    def obtener_historial_movimientos(self):
       """Retorna todos los movimientos en los que participó este elemento"""
       return DetalleMovimiento.objects.filter(elemento=self).select_related('movimiento').order_by('-movimiento__fecha_movimiento','-movimiento__hora_movimiento','-movimiento__id')    

    def asignar_usuario(self, usuario):
        """Asigna el elemento a un usuario"""
        self.usuario_actual = usuario
        self.estado = 'Asignado'
        self.save()


    def liberar(self):
        """Libera el elemento (lo deja disponible)"""
        self.usuario_actual = None
        self.estado = 'Disponible'
        self.save()

    def enviar_mantenimiento(self):
        """Envía el elemento a mantenimiento"""
        self.estado = 'Mantenimiento'
        self.save()

    def dar_baja(self):
        """Da de baja el elemento"""
        self.estado = 'Baja'
        self.usuario_actual = None
        self.save()    

@receiver(pre_delete, sender=MovimientoInventario)
def deshacer_movimiento_al_eliminar(sender, instance, **kwargs):
    # 1. Buscamos todos los elementos involucrados en este movimiento a punto de morir
    detalles = DetalleMovimiento.objects.filter(movimiento=instance)
    
    # 2. Recorremos cada elemento y lo "Liberamos"
    for detalle in detalles:
        elemento = detalle.elemento
        
        # Usamos la función que ya tienes creada en tu modelo Elemento
        elemento.liberar() 
        # Nota: Esto devolverá el elemento al estado 'Disponible' y le quitará el usuario.
