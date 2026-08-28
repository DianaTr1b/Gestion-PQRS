from django.db import models

class EstadoChoices(models.TextChoices):
    ACTIVO = 'Activo', 'Activo'
    INACTIVO = 'Inactivo', 'Inactivo'

class BodegaChoices(models.TextChoices):
    PRINCIPAL_BOGOTA = 'Principal Bogotá', 'Principal Bogotá'
    AGENCIA_BUENAVENTURA = 'Agencia Buenaventura', 'Agencia Buenaventura'
    AGENCIA_CARTAGENA = 'Agencia Cartagena', 'Agencia Cartagena'

class EstadoEquipo(models.TextChoices):
    OPTIMO = 'Óptimo', 'Óptimo'
    REGULAR = 'Regular', 'Regular'
    DEFICIENTE = 'Deficiente', 'Deficiente'

class Ubicacion(models.TextChoices):
    BOGOTA = 'Bogotá', 'Bogotá'
    BUENAVENTURA = 'Buenaventura', 'Buenaventura'
    CALI = 'Cali', 'Cali'
    CARTAGENA = 'Cartagena', 'Cartagena'
    CUCUTA = 'Cúcuta', 'Cúcuta'
    MEDELLIN = 'Medellín', 'Medellín'
    YOPAL = 'Yopal', 'Yopal'
    
class UbicacionBodega(models.TextChoices):
    BOGOTA = 'Bogotá', 'Bogotá'
    BUENAVENTURA = 'Buenaventura', 'Buenaventura'
    CARTAGENA = 'Cartagena', 'Cartagena'