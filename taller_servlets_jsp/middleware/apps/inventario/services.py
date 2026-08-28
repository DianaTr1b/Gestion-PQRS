from django.db import transaction
from .utils import procesar_firma_con_fondo_blanco

@transaction.atomic
def guardar_firma_acta(movimiento, tipo_firma, firma_data):
    """
    Recibe la imagen procesada y la asigna al campo correcto en la Base de Datos.
    """
    archivo_imagen = procesar_firma_con_fondo_blanco(firma_data)
    nombre_archivo = f'firma_{tipo_firma}_mov{movimiento.id}.png'

    if tipo_firma == 'recibe':
        movimiento.firma_recibe.save(nombre_archivo, archivo_imagen, save=False)
    elif tipo_firma == 'elabora':
        movimiento.firma_elabora.save(nombre_archivo, archivo_imagen, save=False)
    elif tipo_firma == 'autoriza':
        movimiento.firma_autoriza.save(nombre_archivo, archivo_imagen, save=False)

    tiene_recibe  = bool(movimiento.firma_recibe)
    tiene_elabora = bool(movimiento.firma_elabora)
    tiene_autoriza = bool(movimiento.firma_autoriza)
    
    if tiene_recibe and tiene_elabora and tiene_autoriza:
        movimiento.es_firmado_total = True

    movimiento.save()
    
    return movimiento