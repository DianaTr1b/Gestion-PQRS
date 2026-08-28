import base64
from PIL import Image as PILImage
import io as python_io
from django.core.files.base import ContentFile

def procesar_firma_con_fondo_blanco(firma_data):
    """
    Toma el base64 de la firma, le pone un fondo blanco y devuelve un archivo.
    """
    formato, imgstr = firma_data.split(';base64,')
    img_bytes = base64.b64decode(imgstr)
    
    img = PILImage.open(python_io.BytesIO(img_bytes)).convert('RGBA')

    fondo = PILImage.new('RGBA', img.size, (255, 255, 255, 255))
    fondo.paste(img, mask=img.split()[3])
    fondo = fondo.convert('RGB')

    img_buffer = python_io.BytesIO()
    fondo.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return ContentFile(img_buffer.read())