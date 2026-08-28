# Módulo Web: Gestión de Inventario (Adaptación Académica)

Este repositorio contiene el módulo web desarrollado como evidencia para el programa ADSO del SENA.

## Nota Técnica de Homologación (Java a Python/Django)
De acuerdo con los lineamientos, el taller requiere el uso de Servlets, JSP y peticiones GET/POST. Por coherencia técnica con la fase anterior, el equipo homologó estas tecnologías utilizando el framework **Django**, demostrando los mismos patrones arquitectónicos:

1. **Servlets y Métodos GET/POST:** En lugar de usar Java Servlets, el sistema utiliza las **Vistas (Views)** de Django (ubicadas en `views.py`). Estas funciones reciben los objetos `request` e implementan lógica condicional (ej. `if request.method == 'POST':`) para procesar los formularios HTML y realizar la inserción o actualización en la base de datos, mientras que las peticiones `GET` se encargan de renderizar los formularios vacíos y las listas.
2. **Elementos JSP (JavaServer Pages):** La función de inyectar lógica de servidor en el HTML que provee JSP se reemplazó por el **Motor de Plantillas de Django (Django Templates)**. Los archivos `.html` del proyecto utilizan etiquetas de servidor como `{% for %}`, `{% if %}` y variables dinámicas como `{{ movimiento.id }}` para renderizar datos desde el backend directamente en el frontend.
3. **Formularios HTML:** Todo el módulo interactúa a través de formularios semánticos y responsivos que envían datos seguros mediante tokens CSRF al servidor.