import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)
def _enviar_correo_hilo(email):
    """
    Función interna para ejecutar el envío en un hilo separado.
    """
    try:
        email.send(fail_silently=False)
        logger.info(f"Correo enviado a {email.to}")
    except Exception as e:
        error_msg = f"ERROR CRITICO SMTP en hilo asíncrono{str(e)}"
        print(error_msg)
        logger.error(error_msg)

def enviar_notificacion_movimiento(movimiento):
    """
    Envía notificaciones por correo a todos los involucrados de forma asíncrona.
    """
    destinatarios = set()
    participantes = [
        movimiento.usuario_registro,
        movimiento.usuario_origen,
        movimiento.usuario_destino,
        movimiento.usuario_autoriza
    ]
    
    for perfil in participantes:
        if perfil and hasattr(perfil, 'user') and perfil.user.email:
            destinatarios.add(perfil.user.email)
    
    if not destinatarios:
        return False

    context = {
        'movimiento': movimiento,
        'base_url': settings.BASE_URL,
        'elementos': movimiento.detalles.all()
    }
    
    html_template = 'apps/inventario/emails/notificacion_movimiento.html'
    
    try:
        html_content = render_to_string(html_template, context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=f'📦 Nuevo Movimiento #{movimiento.id} - {movimiento.get_tipo_movimiento_display()}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=list(destinatarios)
        )
        email.attach_alternative(html_content, "text/html")
        
        # ---MEJORA PRO: ENVÍO ASÍNCRONO ---
        thread = threading.Thread(target=_enviar_correo_hilo, args=(email,))
        thread.start()
        #_enviar_correo_hilo(email)
        # --------------------------------------
        
        return True
    except Exception as e:
        print(f"Error al preparar notificación: {str(e)}")
        return False

def enviar_recordatorio_firma(movimiento, usuario_perfil):
    """
    Envía recordatorio de firma de forma asíncrona.
    """
    if not usuario_perfil or not usuario_perfil.user.email:
        return False
    
    context = {
        'movimiento': movimiento,
        'usuario': usuario_perfil,
        'base_url': settings.BASE_URL
    }
    
    try:
        html_content = render_to_string('apps/inventario/emails/recordatorio_firma.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=f'⏰ Recordatorio: Firma Pendiente - Movimiento #{movimiento.id}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[usuario_perfil.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Envío asíncrono
        threading.Thread(target=_enviar_correo_hilo, args=(email,)).start()
        return True
    except Exception as e:
        print(f"Error al preparar recordatorio: {str(e)}")
        return False

def enviar_notificacion_firma(usuario, documento):
    """
    Función de compatibilidad.
    """
    if hasattr(documento, 'tipo_movimiento'):
        return enviar_recordatorio_firma(documento, usuario)
    return False