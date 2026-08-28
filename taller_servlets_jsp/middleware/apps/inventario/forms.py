from django import forms
from django.core.exceptions import ValidationError
from .models import Elemento, MovimientoInventario, DetalleMovimiento, Categoria, NombreElemento
from apps.usuarios.models import PerfilUsuario
from django.db.models import Q

class ElementoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        cat_nombre = obj.categoria.nombre.lower() if obj.categoria else ""
        
        # Regla blindada para Software
        if 'suscripcion' in str(obj.condicion).lower() or 'software' in cat_nombre or 'licencia' in cat_nombre:
            info = obj.cuenta_asociada if obj.cuenta_asociada else "Sin correo"
        else:
            info = f"{obj.marca} {obj.modelo}".strip()
            if not info or info == "None None": 
                info = "Sin detalles técnicos"
                
        nombre = obj.nombre_elemento.nombre if obj.nombre_elemento else "Elemento"
        estado_visible = obj.get_estado_display() if hasattr(obj, 'get_estado_display') else obj.estado
        return f"[{obj.id}] {nombre} - {info} ({estado_visible})"

def etiqueta_elemento_personalizada(obj):
    """Muestra el correo para software y marca/modelo para hardware."""
    # Verificamos directamente la Condición en lugar del nombre de la categoría
    if obj.condicion == 'Suscripcion':
        identificador = obj.cuenta_asociada if obj.cuenta_asociada else "Sin correo"
    else:
        identificador = f"{obj.marca} {obj.modelo}"
    
    nombre = obj.nombre_elemento.nombre if hasattr(obj, 'nombre_elemento') and obj.nombre_elemento else "Elemento"
    estado_visible = obj.get_estado_display() if hasattr(obj, 'get_estado_display') else obj.estado
    return f"[{obj.id}] - {nombre} ({identificador}) - {estado_visible}"

class ElementoForm(forms.ModelForm):
    """
    Formulario para crear y editar elementos del inventario
    """

    nombre_elemento = forms.ModelChoiceField(
        queryset = NombreElemento.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Nombre del Elemento',
        required = True
    )

    operador = forms.CharField(
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='Operador'
    )

    numero = forms.CharField(
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='Numero'
    )

    capacidad = forms.CharField(
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='Capacidad'
    )

    tipo = forms.CharField(
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='tipo'
    )

    caracteristica = forms.CharField(
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='caracteristica'
    )

    puertos = forms.CharField(
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='Puertos'
    )

    mac = forms.CharField(
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        label='Direccion MAC'
    )

    class Meta:
        model = Elemento
        fields = [
            'categoria','id', 'nombre_elemento','compania', 'marca', 'modelo',
            'serial', 'imei','imei_2','color',
            'operador','numero','capacidad','tipo','caracteristica','puertos',
            'mac','descripcion','fecha_compra','garantia_hasta',
            'factura','documento_adicional', 'usuario_registro', 'bodega_actual',
            'condicion','periodicidad_pago','elemento_padre', 'cuenta_asociada',
            'tipo_cuenta'
        ]
        widgets = {
            'id': forms.TextInput(attrs={   
                'class': 'form-control',
                'inputmode':'numeric',
                'pattern':'[0-9]*',
                'placeholder': 'Solo números',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del elemento'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca del elemento'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo'
            }),
            'serial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie'
            }),
            'imei': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IMEI (para dispositivos móviles)'
            }),
            'imei_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional'
            }),
            
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_compra': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'garantia_hasta': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'usuario_registro': forms.Select(attrs={
                'class': 'form-select'
            }),
            'bodega_actual': forms.Select(attrs={
                'class': 'form-select'
            }),
            'compania': forms.Select(attrs={
                'class': 'form-select'
            }),
            'condicion': forms.Select(attrs={
                    'class': 'form-select'
            }),
            'periodicidad_pago': forms.Select(attrs={
                    'class': 'form-select'
            }),
            'tipo_cuenta': forms.Select(attrs={
                    'class': 'form-select'
            }),
            'cuanta_asociada': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Correo asociado'
            }),
            'elemento_padre': forms.Select(attrs={
                    'class': 'form-select'
            }),
            'fecha_compra': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'garantia_hasta': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Negro, Gris, Blanco'}),
        }
        labels = {
            'id': 'ID del Elemento',  # CAMBIO: Label para ID
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'serial': 'Serial',
            'imei': 'IMEI',         
            'estado': 'Estado',
            'fecha_compra': 'Fecha de Compra',
            'garantia_hasta': 'Garantía Hasta',
            'usuario_registro': 'Usuario que Registra',
            'condicion': 'Condición del Elemento',
            'periodicidad_pago': 'Periodicidad de Pago',
            'tipo_cuenta': 'Tipo de Cuenta (Solo para Software)',
            'cuenta_asociada': 'Correo Asociado (Solo para Software)',
            'elemento_padre': 'Elemento Padre',
            'fectura': 'Factura de Compra',
            'garantia_hasta': 'Garantía Hasta',
        }
    
    def __init__(self, *args, **kwargs):
        self._usuario_actual = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        self.fields['garantia_hasta'].required = False
        
        if 'tipo_cuenta' in self.fields:
            self.fields['tipo_cuenta'].widget.attrs.update({'class': 'form-select'})

        # Filtrar solo categorías activas
        self.fields['categoria'].queryset = Categoria.objects.filter(estado='Activo')
        # Filtro para mostrar solo Cuentas Principales de Software
        if 'elemento_padre' in self.fields:
            from .models import Elemento
            self.fields['elemento_padre'].queryset = Elemento.objects.filter(
                condicion='Suscripcion',
                elemento_padre__isnull=True
            )
            self.fields['elemento_padre'].empty_label = "--- Principal (Esta es la cuenta maestra) ---"
            self.fields['elemento_padre'].widget.attrs.update({'class': 'form-select'})
            
        if 'cuenta_asociada' in self.fields:
            self.fields['cuenta_asociada'].widget.attrs.update({'class': 'form-control'})

        # CAMBIO: Filtrar solo usuarios con rol "Bodega" y estado Activo
        self.fields['bodega_actual'].queryset = PerfilUsuario.objects.filter(
            rol__nombre='Bodega',
            estado='Activo'
        ).select_related('user','rol')

        if hasattr(self, '_usuario_actual') and self._usuario_actual:
            self.fields['usuario_registro'].initial = self._usuario_actual
            self.fields['usuario_registro'].widget = forms.Select(attrs={
                'class': 'form-select',
                'style':'pointer-events: none; background-color: #e9ecef;'
            })
            self.fields['usuario_registro'].required = True
            self.fields['usuario_registro'].queryset = PerfilUsuario.objects.filter(
                id=self._usuario_actual.id
            )
        else:
            self.fields['usuario_registro'].queryset = PerfilUsuario.objects.filter(
                rol__nombre='Técnico', estado='Activo'
            ).select_related('user', 'rol')

        if self.instance.pk and hasattr(self.instance,'nombre_elemento'):
            nombre_elemento=self.instance.nombre_elemento
            self._configurar_campos_requeridos(nombre_elemento)
        elif'nombre_elemento' in self.data:
            try:
                nombre_elemento_id = int(self.data.get('nombre_elemento'))
                nombre_elemento = NombreElemento.objects.get(pk=nombre_elemento_id)
                self._configurar_campos_requeridos(nombre_elemento)
            except (ValueError,TypeError, NombreElemento.DoesNotExist):
                pass        

        if 'categoria' in self.data:
            try: 
                categoria_id = int(self.data.get('categoria'))
                self.fields['nombre_elemento'].queryset =NombreElemento.objects.filter(
                    categoria_id=categoria_id,
                    activo=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.categoria:
            self.fields['nombre_elemento'].queryset =NombreElemento.objects.filter(
                categoria=self.instance.categoria,
                activo=True
            )
        if 'elemento_padre' in self.fields:
            self.fields['elemento_padre'].label_from_instance = etiqueta_elemento_personalizada
    
    def clean_id(self):
        """Validar que el ID sea único y numérico"""
        elemento_id = self.cleaned_data.get('id')
        if elemento_id:
            if not elemento_id.isdigit():
                raise ValidationError('El ID debe contener solo números.')
            elementos = Elemento.objects.filter(id=elemento_id)
            if self.instance.pk:
                elementos = elementos.exclude(pk=self.instance.pk)
            if elementos.exists():
                raise ValidationError('Ya existe un elemento con este ID.')
        return elemento_id

    def clean_serial(self):
        """Validar que el serial sea único si se proporciona"""
        serial = self.cleaned_data.get('serial')
        if serial and serial.strip().upper() in ['N/R', 'NR', 'NO REGISTRA', 'N/A']:
            return None
        if serial:
            # Excluir el elemento actual si estamos editando
            elementos = Elemento.objects.filter(serial=serial)
            if self.instance.pk:
                elementos = elementos.exclude(pk=self.instance.pk)
            
            if elementos.exists():
                raise ValidationError('Ya existe un elemento con este serial.')
        return serial

    def _configurar_campos_requeridos(self, nombre_elemento):
        """
        Configura qué campos son requeridos según el tipo de elemento
        """
        # Serial
        self.fields['serial'].required = nombre_elemento.requiere_serial
        
        # IMEI
        self.fields['imei'].required = nombre_elemento.requiere_imei
        
        # IMEI2
        self.fields['imei_2'].required = nombre_elemento.requiere_imei2
        
        # Color
        self.fields['color'].required = nombre_elemento.requiere_color
        
        # Marca
        self.fields['marca'].required = nombre_elemento.requiere_marca
        
        # Modelo
        self.fields['modelo'].required = nombre_elemento.requiere_modelo
        
        # Operador
        self.fields['operador'].required = nombre_elemento.requiere_operador
        
        # Número
        self.fields['numero'].required = nombre_elemento.requiere_numero
        
        # Capacidad
        self.fields['capacidad'].required = nombre_elemento.requiere_capacidad
        
        # Tipo
        self.fields['tipo'].required = nombre_elemento.requiere_tipo
        
        # Característica
        self.fields['caracteristica'].required = nombre_elemento.requiere_caracteristica
        
        # Puertos
        self.fields['puertos'].required = nombre_elemento.requiere_puertos
        
        # MAC
        self.fields['mac'].required = nombre_elemento.requiere_mac

    def clean(self):
        """Validaciones generales del formulario"""
        cleaned_data = super().clean()
        
        condicion = cleaned_data.get('condicion')
        fecha_compra = cleaned_data.get('fecha_compra')
        garantia_hasta = cleaned_data.get('garantia_hasta')
        
        # Campos de software
        cuenta_asociada = cleaned_data.get('cuenta_asociada')
        nombre_elemento = cleaned_data.get('nombre_elemento')
        tipo_cuenta = cleaned_data.get('tipo_cuenta')

        # 1. Lógica para RENTADO
        if condicion == 'Rentado' and not garantia_hasta:
            if fecha_compra:
                cleaned_data['garantia_hasta'] = fecha_compra
                if self.instance:
                    self.instance.garantia_hasta = fecha_compra

        # 2. Lógica para SOFTWARE
        elif condicion == 'Suscripcion':
            if not garantia_hasta:
                self.add_error('garantia_hasta', 'La fecha de próxima renovación es obligatoria.')
            
            # 🔴 NUEVO: ¡Obligar a llenar los campos!
            if not tipo_cuenta:
                self.add_error('tipo_cuenta', 'Debe seleccionar si es Cuenta Principal o Subcuenta.')
            if not cuenta_asociada:
                self.add_error('cuenta_asociada', 'El correo asociado es obligatorio para el software.')
            
            # CANDADO: Correos únicos
            if tipo_cuenta == 'Principal' and cuenta_asociada and nombre_elemento:
                from .models import Elemento
                duplicado = Elemento.objects.filter(
                    condicion='Suscripcion',
                    tipo_cuenta='Principal',
                    nombre_elemento=nombre_elemento,
                    cuenta_asociada__iexact=cuenta_asociada.strip()
                )
                
                # Esto soluciona el fallo: Solo excluir si el elemento ya existe (edición)
                if self.instance and self.instance.pk:
                    duplicado = duplicado.exclude(pk=self.instance.pk)
                    
                if duplicado.exists():
                    self.add_error('cuenta_asociada', f'El correo "{cuenta_asociada}" ya está registrado como cuenta principal para {nombre_elemento.nombre}.')

        # 3. Lógica para PROPIO
        else:
            if fecha_compra and garantia_hasta and garantia_hasta < fecha_compra:
                self.add_error('garantia_hasta', 'La fecha de garantía no puede ser anterior a la fecha de compra.')

        return cleaned_data

class MovimientoInventarioForm(forms.ModelForm):
    """
    Formulario para crear movimientos de inventario
    """
    class Meta:
        model = MovimientoInventario
        fields = [
            'tipo_movimiento', 'usuario_origen', 'usuario_destino',
            'usuario_registro','usuario_autoriza','estado_movimiento', 'observaciones'
        ]
        widgets = {
            'tipo_movimiento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_movimiento'
            }),
            'usuario_origen': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_usuario_origen'
            }),
            'usuario_destino': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_usuario_destino'
            }),
            
            'usuario_registro': forms.Select(attrs={'class': 'form-select'}),
            'usuario_autoriza': forms.Select(attrs={'class': 'form-select','id': 'id_usuario_autoriza'}),
            'estado_movimiento': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales del movimiento'
            }),
            'documento_soporte': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self._usuario_actual = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        self.fields['usuario_registro'].queryset = PerfilUsuario.objects.filter(
            rol__nombre='Técnico',
            estado='Activo'
        ).select_related('rol')

        self.fields['usuario_autoriza'].queryset = PerfilUsuario.objects.filter(
            puede_autorizar=True,
            estado='Activo'  
        ).select_related('user', 'rol')
        self.fields['usuario_autoriza'].required = False    
        
        # hacer campos opcionales en el formulario
        if hasattr(self, '_usuario_actual') and self._usuario_actual:
            self.fields['usuario_registro'].initial = self._usuario_actual
            self.fields['usuario_registro'].widget = forms.Select(attrs={
                'class': 'form-select',
                'style':'pointer-events: none; background-color: #e9ecef;'
            })
            self.fields['usuario_registro'].required = True
            self.fields['usuario_registro'].queryset = PerfilUsuario.objects.filter(
                id=self._usuario_actual.id
            )

            self.fields['estado_movimiento'].initial = 'Pendiente'
            self.fields['estado_movimiento'].widget.attrs.update({
            'style': 'pointer-events: none; background-color: #e9ecef;'
            })
        self.fields['usuario_origen'].required = False
        self.fields['usuario_destino'].required = False
        self.fields['usuario_origen'].queryset = PerfilUsuario.objects.filter(estado='Activo', user__is_active=True).select_related('rol')
        self.fields['usuario_destino'].queryset = PerfilUsuario.objects.filter(estado='Activo', user__is_active=True).select_related('rol')

    def clean(self):
        cleaned_data = super().clean()
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        usuario_origen = cleaned_data.get('usuario_origen')
        usuario_destino = cleaned_data.get('usuario_destino')

        if tipo_movimiento in ['Asignacion', 'Reasignacion', 'Devolucion', 'Baja']:
            if not usuario_origen:
                raise ValidationError({
                    'usuario_origen': f'Este tipo de movimiento requiere un Usuario Origen.'
                })

        if tipo_movimiento in ['Asignacion', 'Reasignacion', 'Baja']:
            if not usuario_destino:
                raise ValidationError({
                    'usuario_destino': f'Este tipo de movimiento requiere un Usuario Destino.'
                })

        if tipo_movimiento == 'Asignacion':
            if usuario_origen and usuario_origen.rol.nombre != 'Bodega':
                raise ValidationError({
                    'usuario_origen': 'Para Asignación el origen debe ser un usuario con rol Bodega.'
                })

        if tipo_movimiento in ['Devolucion', 'Baja']:
            if usuario_destino and usuario_destino.rol.nombre != 'Bodega':
                raise ValidationError({
                    'usuario_destino': 'El destino debe ser un usuario con rol Bodega.'
                })
            
        if tipo_movimiento == 'Mantenimiento':
            if usuario_destino and usuario_destino.rol.nombre != 'Bodega':
                raise ValidationError({
                    'usuario_destino': 'Para Mantenimiento el destino debe ser un usuario con rol Bodega.'
                })    

        if tipo_movimiento == 'Baja':
            if usuario_origen and usuario_origen.rol.nombre != 'Bodega':
                raise ValidationError({
                    'usuario_origen': 'Para Baja el origen debe ser un usuario con rol Bodega.'
                })

        return cleaned_data
            
        # if tipo_movimiento == 'Devolucion':
        #     if usuario_destino and usuario_destino.rol.nombre != 'Bodega':
        #         raise ValidationError({
        #             'usuario_destino': 'Para una Devoluvión el destino debe ser un usuario con rol Bodega.'})    

        #return cleaned_data


class DetalleMovimientoForm(forms.ModelForm):
    """
    Formulario para los detalles de cada elemento en un movimiento
    """
    elemento = ElementoChoiceField(
        queryset=Elemento.objects.filter(estado='Disponible'),
        widget=forms.Select(attrs={'class': 'form-select elemento-select'}),
        label='Elemento',
        required=False
    )
    class Meta:
        model = DetalleMovimiento
        fields = [
            'elemento', 'estado_elemento_antes',
            'estado_elemento_despues', 'observaciones_elemento'
        ]
        widgets = {
            'elemento': forms.Select(attrs={
                'class': 'form-select elemento-select'
            }),

            'estado_elemento_antes': forms.Select(attrs={'class': 'form-select'}),
            'estado_elemento_despues': forms.Select(attrs={'class': 'form-select'}),
            'estado_posterior': forms.Select(attrs={'class': 'form-select', 'required':'required'}),
            'observaciones_elemento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones específicas de este elemento'
            }),
        }

        labels ={
            'estado_elemento_despues': ' Estado del Elemento',
            'elemento':'Seleccionar Equipo',
        }

    def __init__(self, *args, tipo_movimiento=None, usuario_origen=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tipo_movimiento = tipo_movimiento

        if 'elemento' in self.fields:
            # self.fields['elemento'].queryset = Elemento.objects.filter(estado='Disponible')
            self.fields['elemento'].queryset = Elemento.objects.all()
            self.fields['elemento'].widget.attrs.update({'class': 'form-select elemento-select'})

        if 'estado_elemento_despues' in self.fields:
            self.fields['estado_elemento_despues'].required = True
        
        if 'elemento' in self.fields:
            self.fields['elemento'].required = True
            regla_busqueda = ~Q(detalles_movimiento__movimiento__estado_movimiento='Pendiente')
            if self.instance and self.instance.pk and self.instance.elemento_id:
                regla_busqueda = regla_busqueda | Q(id=self.instance.elemento_id)

            self.fields['elemento'].queryset = Elemento.objects.filter(regla_busqueda).distinct()    

            # FORZAR ETIQUETA: Regla activada obligatoriamente para formsets
            def etiqueta_dinamica(obj):
                cat_nombre = obj.categoria.nombre.lower() if obj.categoria else ""
                
                # Si es software o suscripción, muestra el correo
                if 'suscripcion' in str(obj.condicion).lower() or 'software' in cat_nombre or 'licencia' in cat_nombre:
                    info = obj.cuenta_asociada.strip() if obj.cuenta_asociada and obj.cuenta_asociada.strip() else "Sin correo"
                else:
                    info = f"{obj.marca or ''} {obj.modelo or ''}".strip()
                    if not info or info == "None None": 
                        info = "Sin detalles técnicos"
                        
                nombre = obj.nombre_elemento.nombre if obj.nombre_elemento else "Elemento"
                estado_visible = obj.get_estado_display() if hasattr(obj, 'get_estado_display') else obj.estado
                return f"[{obj.id}] {nombre} - {info} ({estado_visible})"
            
            # Aplicamos la regla dinámicamente
            self.fields['elemento'].label_from_instance = etiqueta_dinamica

        # Aplicar clases de Bootstrap al resto de campos
        if 'cantidad' in self.fields:
            self.fields['cantidad'].widget.attrs.update({'class': 'form-control'})
            self.fields['cantidad'].initial = 1
            self.fields['cantidad'].required = False
        if 'observaciones_elemento' in self.fields:
            self.fields['observaciones_elemento'].widget.attrs.update({'class': 'form-control', 'rows': '2'})
        
  


    def clean_elemento(self):
        elemento=self.cleaned_data.get('elemento')
        tipo =self.tipo_movimiento

        if not elemento:
            return None
            
        if tipo in ['Devolucion','Reasignacion']:
            if elemento.estado != 'Asignado':
                raise ValidationError('Para este movimiento el elemento debe estar asignado')
        elif tipo == 'Asignacion':
            if elemento.estado != 'Disponible':
                raise ValidationError('Para Asignación este el elemento debe estar disponible')  
        return elemento
    
    def has_changed(self):
        """ignorar formularios complemente vacíos"""
        elemento_key = self.add_prefix('elemento')
        elemento_value = self.data.get(elemento_key,'').strip()
        if not elemento_value:
            return False
        return super().has_changed()


# Formset para manejar múltiples detalles en un movimiento
DetalleMovimientoFormSet = forms.inlineformset_factory(
    MovimientoInventario,
    DetalleMovimiento,
    form=DetalleMovimientoForm,
    can_delete=True,
    extra=1,
    max_num=10,
    validate_max=True,
    min_num=1,
    validate_min=False,
    can_delete_extra=True,
)


class BusquedaElementoForm(forms.Form):
    """
    Formulario para búsqueda y filtros de elementos
    """
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, marca, modelo, serial...'
        }),
        label='Búsqueda'
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + Elemento.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Estado'
    )
    categoria = forms.ModelChoiceField(
        required=False,
        queryset=Categoria.objects.filter(estado='Activo'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Categoría',
        empty_label='Todas'
    )
    bodega = forms.ModelChoiceField(
        queryset=PerfilUsuario.objects.filter(
            rol__nombre='Bodega',
            estado='Activo'
        ),
        required=False,
        label='Bodega',
        widget=forms.Select(attrs={'class':'form-select'})
    )


class BusquedaMovimientoForm(forms.Form):
    """
    Formulario para búsqueda y filtros de movimientos
    """
    tipo = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + MovimientoInventario.TIPO_MOVIMIENTO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de Movimiento'
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + MovimientoInventario.ESTADO_MOVIMIENTO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Estado'
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha Desde'
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Fecha Hasta'
    )

    