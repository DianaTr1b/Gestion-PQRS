import io
import os
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import KeepTogether
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable, Image
)


# ── Colores corporativos ────────────────────────────────────────────────────
COLOR_HEADER    = colors.HexColor('#94a3b8') 
COLOR_SECCION   = colors.HexColor('#cbd5e1')
COLOR_FILA_PAR  = colors.HexColor('#f5f5f5')
COLOR_CHIP_BG   = colors.HexColor('#eeeeee')
COLOR_CHIP_TEXT = colors.HexColor('#444444')


# ── Campos técnicos por NombreElemento ─────────────────────────────────────
# Devuelve lista de (label, valor) solo con los campos que tienen contenido.
def _campos_tecnicos(elemento):
    campos = []

    def add(label, valor):
        if valor:
            campos.append((label, str(valor)))

    add('Marca',       elemento.marca)
    add('Modelo',      elemento.modelo)
    add('Serial',      elemento.serial)
    add('IMEI 1',      elemento.imei)
    add('IMEI 2',      elemento.imei_2)
    add('Operador',    elemento.operador)
    add('Número',      elemento.numero)
    add('Capacidad',   elemento.capacidad)
    add('Tipo',        elemento.tipo)
    add('Característica', elemento.caracteristica)
    add('Puertos',     elemento.puertos)
    add('MAC',         elemento.mac)
    add('Compañía',    getattr(elemento, 'compania', None))
    return campos


def generar_acta_movimiento(movimiento):
    """
    Genera el PDF del acta de movimiento.
    Retorna un buffer BytesIO listo para servir.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm,
    )

    # ── Estilos ──────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    def estilo(name, base='Normal', **kw):
        return ParagraphStyle(name, parent=styles[base], **kw)

    E_BLANCO     = estilo('blanco',     fontSize=8,  fontName='Helvetica',      textColor=colors.black)
    E_BLANCO_B   = estilo('blanco_b',   fontSize=8,  fontName='Helvetica-Bold', textColor=colors.black)
    E_BLANCO_T   = estilo('blanco_t',   fontSize=11, fontName='Helvetica-Bold', textColor=colors.black, alignment=TA_CENTER)
    E_TITULO_DOC = estilo('titulo_doc', fontSize=13, fontName='Helvetica-Bold', textColor=colors.black, alignment=TA_CENTER)
    E_MOV_NUM    = estilo('mov_num',    fontSize=10, fontName='Helvetica-Bold', textColor=colors.black, alignment=TA_RIGHT)
    E_MOV_FECHA  = estilo('mov_fecha',  fontSize=8,  fontName='Helvetica',      textColor=colors.HexColor('#555555'), alignment=TA_RIGHT)
    E_SECCION    = estilo('seccion',    fontSize=8,  fontName='Helvetica-Bold', textColor=colors.HexColor('#333333'), alignment=TA_CENTER)
    E_LABEL      = estilo('label',      fontSize=7,  fontName='Helvetica-Bold', textColor=colors.HexColor('#666666'))
    E_VALOR      = estilo('valor',      fontSize=8,  fontName='Helvetica',      textColor=colors.black)
    E_VALOR_C    = estilo('valor_c',    fontSize=8,  fontName='Helvetica',      textColor=colors.black, alignment=TA_CENTER)
    E_CHIP_L     = estilo('chip_l',     fontSize=7,  fontName='Helvetica-Bold', textColor=COLOR_CHIP_TEXT)
    E_CHIP_V     = estilo('chip_v',     fontSize=8,  fontName='Helvetica',      textColor=colors.black)
    E_FIRMA_N    = estilo('firma_n',    fontSize=8,  fontName='Helvetica-Bold', textColor=colors.black, alignment=TA_CENTER)
    E_FIRMA_C    = estilo('firma_c',    fontSize=7,  fontName='Helvetica',      textColor=colors.HexColor('#555555'), alignment=TA_CENTER)
    E_FIRMA_ROL  = estilo('firma_rol',  fontSize=7,  fontName='Helvetica-Bold', textColor=colors.HexColor('#333333'), alignment=TA_CENTER)
    E_PIE        = estilo('pie',        fontSize=7,  fontName='Helvetica',      textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    # ── Datos del movimiento ─────────────────────────────────────────────────
    origen   = movimiento.usuario_origen
    destino  = movimiento.usuario_destino
    registra = movimiento.usuario_registro
    tipo     = movimiento.get_tipo_movimiento_display()
    fecha    = movimiento.fecha_movimiento.strftime('%d/%m/%Y')
    hora     = movimiento.hora_movimiento.strftime('%H:%M') if movimiento.hora_movimiento else ''
    detalles = list(movimiento.detalles.select_related(
        'elemento', 'elemento__categoria', 'elemento__nombre_elemento'
    ).all())

    # ── LOGO ─────────────────────────────────────────────────────────────────
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static', 'img', 'LOGO_BLACK.png'
    )
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=4 * cm, height=1.4 * cm)
    else:
        logo = Paragraph('ECL-TOTAL', E_BLANCO_T)

    # ── ENCABEZADO ───────────────────────────────────────────────────────────
    header_data = [[
        logo,
        Paragraph('ACTA DE MOVIMIENTO DE INVENTARIO', E_TITULO_DOC),
        [
            Paragraph(f'N° MOV-{movimiento.id}', E_MOV_NUM),
            Paragraph(f'{fecha}  {hora}', E_MOV_FECHA),
        ],
    ]]
    header = Table(header_data, colWidths=[4.5 * cm, 9 * cm, 4.5 * cm])
    header.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), COLOR_HEADER),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWPADDING',  (0, 0), (-1, -1), 10),
        ('GRID',        (0, 0), (-1, -1), 0.3, colors.HexColor('#333355')),
    ]))

    # ── TIPO DE MOVIMIENTO ───────────────────────────────────────────────────
    tipo_row = Table(
        [[Paragraph(f'TIPO DE MOVIMIENTO: {tipo.upper()}', E_SECCION)]],
        colWidths=[18 * cm]
    )
    tipo_row.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_SECCION),
        ('ROWPADDING', (0, 0), (-1, -1), 5),
    ]))

    # ── USUARIOS ORIGEN / DESTINO ────────────────────────────────────────────
    def _nombre(u):  return u.nombre if u else '—'
    def _cargo(u):   return u.cargo_contrato or 'No aplica' if u and u.rol else '—'

    datos_usuarios = Table([
        [
            Paragraph('USUARIO ORIGEN', E_SECCION), '',
            Paragraph('USUARIO DESTINO / RECIBE', E_SECCION), '',
        ],
        [
            Paragraph('Nombre:', E_LABEL),  Paragraph(_nombre(origen),  E_VALOR),
            Paragraph('Nombre:', E_LABEL),  Paragraph(_nombre(destino), E_VALOR),
        ],
        [
            Paragraph('Cargo:', E_LABEL),   Paragraph(_cargo(origen),   E_VALOR),
            Paragraph('Cargo:', E_LABEL),   Paragraph(_cargo(destino),  E_VALOR),
        ],
    ], colWidths=[2.2 * cm, 6.8 * cm, 2.2 * cm, 6.8 * cm])

    datos_usuarios.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (1, 0), COLOR_SECCION),
        ('BACKGROUND',  (2, 0), (3, 0), COLOR_SECCION),
        ('SPAN',        (0, 0), (1, 0)),
        ('SPAN',        (2, 0), (3, 0)),
        ('GRID',        (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('ROWPADDING',  (0, 0), (-1, -1), 5),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND',  (0, 2), (-1, 2), COLOR_FILA_PAR),
    ]))

    # ── SECCIÓN ELEMENTOS ────────────────────────────────────────────────────
    elem_header = Table(
        [[Paragraph('ELEMENTOS DEL MOVIMIENTO', E_SECCION)]],
        colWidths=[18 * cm]
    )
    elem_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_SECCION),
        ('ROWPADDING', (0, 0), (-1, -1), 5),
    ]))

    # Construir una tabla por elemento
    tablas_elementos = []
    for i, detalle in enumerate(detalles):
        e = detalle.elemento
        campos = _campos_tecnicos(e)
        fila_bg = colors.white if i % 2 == 0 else COLOR_FILA_PAR

        # Fila de encabezado del elemento
        cat_nombre = e.categoria.nombre if e.categoria else '—'
        encabezado_elem = Table([[
            Paragraph(str(i + 1), E_BLANCO_B),
            Paragraph(e.nombre or '—', E_BLANCO_B),
            Paragraph(cat_nombre, E_BLANCO),
            Paragraph(f'ID: {e.id}', E_BLANCO),
        ]], colWidths=[0.8 * cm, 7 * cm, 5.5 * cm, 4.7 * cm])
        encabezado_elem.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_SECCION),
            ('ROWPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        # Chips de campos técnicos en grilla de 3 columnas
        # Agregar Estado siempre
        campos_con_estado = campos + [('Estado', e.estado or '—')]
        # Observaciones al final si existen
        if detalle.observaciones_elemento:
            campos_con_estado.append(('Observaciones', detalle.observaciones_elemento))

        # Armar filas de 3 chips cada una
        chip_rows = []
        row_actual = []
        for label, valor in campos_con_estado:
            chip_data = Table([
                [Paragraph(label, E_CHIP_L)],
                [Paragraph(valor, E_CHIP_V)],
            ], colWidths=[5.7 * cm])
            chip_data.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_CHIP_BG),
                ('ROWPADDING', (0, 0), (-1, -1), 3),
                ('GRID',       (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
            ]))
            row_actual.append(chip_data)
            if len(row_actual) == 3:
                chip_rows.append(row_actual)
                row_actual = []
        # Completar última fila con celdas vacías
        if row_actual:
            while len(row_actual) < 3:
                row_actual.append('')
            chip_rows.append(row_actual)

        tabla_chips = Table(chip_rows, colWidths=[5.9 * cm, 5.9 * cm, 5.9 * cm])
        tabla_chips.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), fila_bg),
            ('ROWPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
        ]))

        tablas_elementos.append(encabezado_elem)
        tablas_elementos.append(tabla_chips)

    # ── OBSERVACIONES GENERALES ───────────────────────────────────────────────
    obs_header = Table(
        [[Paragraph('OBSERVACIONES GENERALES', E_SECCION)]],
        colWidths=[18 * cm]
    )
    obs_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_SECCION),
        ('ROWPADDING', (0, 0), (-1, -1), 5),
    ]))
    obs_body = Table(
        [[Paragraph(movimiento.observaciones or 'Sin observaciones.', E_VALOR)]],
        colWidths=[18 * cm]
    )
    obs_body.setStyle(TableStyle([
        ('GRID',       (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
        ('ROWPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
    ]))

    # ── FIRMAS ────────────────────────────────────────────────────────────────
    firmas_header = Table(
        [[Paragraph('FIRMAS', E_SECCION)]],
        colWidths=[18 * cm]
    )
    firmas_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_SECCION),
        ('ROWPADDING', (0, 0), (-1, -1), 5),
    ]))

    # 1. Definimos las variables del autorizador extrayéndolas del movimiento
    autoriza = movimiento.usuario_autoriza
    nombre_autoriza = autoriza.nombre if autoriza else '— Por definir —'
    cargo_autoriza  = autoriza.cargo_contrato or 'No aplica' if autoriza and autoriza.rol else '—'

    # 2. Definimos las variables de quien registra
    nombre_registra = registra.nombre if registra else '—'
    cargo_registra  = registra.cargo_contrato or 'No aplica' if registra and registra.rol else '—'

    # 3. Solo UNA definición de la función de imagen
    def _imagen_firma(campo_firma, ancho=5*cm, alto=1.5*cm):
        """Carga la imagen de firma si existe, si no retorna línea vacía."""
        if campo_firma and hasattr(campo_firma, 'path'):
            try:
                return Image(campo_firma.path, width=ancho, height=alto)
            except:
                pass
        return Paragraph('___________________________', E_FIRMA_C)

    firmas_body = Table([
        [
            _imagen_firma(movimiento.firma_recibe),
            _imagen_firma(movimiento.firma_autoriza),
            _imagen_firma(movimiento.firma_elabora),
        ],
        [
            Paragraph(_nombre(destino),   E_FIRMA_N),
            Paragraph(nombre_autoriza,    E_FIRMA_N),
            Paragraph(nombre_registra,    E_FIRMA_N),
        ],
        [
            Paragraph(_cargo(destino),  E_FIRMA_C),
            Paragraph(cargo_autoriza,   E_FIRMA_C),
            Paragraph(cargo_registra,   E_FIRMA_C),
        ],
        [
            Paragraph('RECIBE',           E_FIRMA_ROL),
            Paragraph('AUTORIZADO POR',   E_FIRMA_ROL),
            Paragraph('ELABORADO POR',    E_FIRMA_ROL),
        ],
        ], colWidths=[6 * cm, 6 * cm, 6 * cm])

    firmas_body.setStyle(TableStyle([
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWPADDING',    (0, 0), (-1, -1), 5),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#eeeeee')),
        ('ROWHEIGHT',     (0, 0), (-1, 0),  3 * cm),
        ('VALIGN',        (0, 0), (-1, 0),  'BOTTOM'),
        ('TOPPADDING',    (0, 0), (-1, 0),  40),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  2),
        ('TOPPADDING',    (0, 1), (-1, 1),  2),
    ]))
    # Fila elaborado por centrada
    # elaborado = Table([[
    #     Paragraph(f'Elaborado por: {nombre_registra} — {cargo_registra}', E_FIRMA_C),
    # ]], colWidths=[18 * cm])
    # elaborado.setStyle(TableStyle([
    #     ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
    #     ('ROWPADDING', (0, 0), (-1, -1), 5),
    #     ('GRID',       (0, 0), (-1, -1), 0.3, colors.HexColor('#eeeeee')),
    # ]))

    # ── PIE ───────────────────────────────────────────────────────────────────
    pie = Paragraph(
        f'Documento generado el {fecha} — Sistema de Inventario ECL-TOTAL — MOV-{movimiento.id}',
        E_PIE
    )

    # ── ARMADO ───────────────────────────────────────────────────────────────
    story = [
        header,
        Spacer(1, 0.3 * cm),
    ]

    # Tipo + usuarios siempre juntos
    story.append(KeepTogether([
        tipo_row,
        Spacer(1, 0.2 * cm),
        datos_usuarios,
    ]))

    story.append(Spacer(1, 0.3 * cm))

    # Encabezado de elementos + cada elemento juntos individualmente
    story.append(elem_header)
    for i in range(0, len(tablas_elementos), 2):
        # Cada elemento son 2 items: encabezado_elem + tabla_chips
        story.append(KeepTogether(tablas_elementos[i:i+2]))

    story.append(Spacer(1, 0.3 * cm))

    # Observaciones juntas
    story.append(KeepTogether([
        obs_header,
        obs_body,
    ]))

    story.append(Spacer(1, 0.1 * cm))

    # Firmas siempre juntas en la misma página
    story.append(KeepTogether([
        firmas_header,
        firmas_body,
        Spacer(1, 0.1 * cm),
        HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc')),
        Spacer(1, 0.1 * cm),
        pie,
    ]))

    doc.build(story)
    buffer.seek(0)
    return buffer