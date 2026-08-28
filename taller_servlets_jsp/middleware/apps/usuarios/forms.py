from django import forms
from django.core.exceptions import ValidationError
from .models import PerfilUsuario, Rol
from apps.inventario.models import Categoria
from django.contrib.auth.models import User

class UsuarioForm(forms.ModelForm):
    """Formulario para crear y editar usuarios"""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'required': 'required'
        }),
        label='Nombre de Usuario'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'required': 'required'
        }),
        label='Correo Electrónico'
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre(s)',
        }),
        label='Nombre(s)',
        required=False
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido(s)',
        }),
        label='Apellido(s)',
        required=False
    )
    
    class Meta:
        model = PerfilUsuario
        fields = ['ciudad', 'rol','estado']
        widgets = {
            'ciudad': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'rol': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
        }
        labels = {
            'ciudad': 'Ciudad',
            'rol': 'Rol',
            'estado': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        
        self.fields['rol'].queryset = Rol.objects.all().order_by('nombre')

    def save(self, commit=True):
        perfil = super().save(commit=False)
        
        # Crear o actualizar User
        if perfil.pk:
            # Actualizar usuario existente
            user = perfil.user
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.is_active = (self.cleaned_data['estado'] == 'Activo')
            if commit:
                user.save()
        else:
            # Crear nuevo usuario
            user = User.objects.create(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                is_active=(self.cleaned_data['estado'] == 'Activo')
            )
            perfil.user = user
        
        if commit:
            perfil.save()
        
        return perfil


class RolForm(forms.ModelForm):
    """Formulario para crear y editar roles"""
    
    class Meta:
        model = Rol
        fields = ['nombre', 'permisos']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del rol',
                'required': 'required'
            }),
            'permisos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción de los permisos del rol',
                'required': 'required'
            }),
        }
        labels = {
            'nombre': 'Nombre del Rol',
            'permisos': 'Descripción de Permisos',
        }

    def clean_nombre(self):
        """Validar que el nombre sea único"""
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            # Excluir el rol actual si estamos editando
            roles = Rol.objects.filter(nombre=nombre)
            if self.instance.pk:
                roles = roles.exclude(pk=self.instance.pk)
            
            if roles.exists():
                raise ValidationError('Ya existe un rol con este nombre.')
        return nombre


class CategoriaForm(forms.ModelForm):
    """Formulario para crear y editar categorías"""
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría',
                'required': 'required'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
        }
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
            'estado': 'Estado',
        }


