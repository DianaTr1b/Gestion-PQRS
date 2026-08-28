# Sistema de Gestión de Inventario (Adaptación Académica)

Este repositorio contiene el módulo de Gestión de Inventario desarrollado como evidencia para el programa Tecnólogo en Análisis y Desarrollo de Software (ADSO) del SENA.

## Nota Técnica Arquitectónica
De acuerdo con los lineamientos del taller, se solicitaba la realización de un CRUD conectado a una base de datos utilizando herramientas como JDBC (Java). Tras una reevaluación técnica y arquitectónica, el equipo de desarrollo decidió implementar esta solución utilizando el framework **Django (Python)**. 

**Justificación técnica:**
1. **Sustitución de JDBC por ORM:** Django incorpora un Mapeador Objeto-Relacional (ORM) nativo que cumple el mismo propósito que JDBC (conectar la lógica de negocio con la base de datos), pero de forma más segura, previniendo ataques de inyección SQL y abstrayendo la complejidad de las consultas.
2. **Operaciones CRUD:** El sistema cumple a cabalidad con las funcionalidades exigidas de Inserción (Crear elementos), Consulta (Listar/Filtrar), Actualización (Editar) y Eliminación (Anular/Dar de baja).
3. **Privacidad de Datos:** Por políticas de protección de datos, la base de datos real y el archivo `.env` han sido excluidos de este repositorio público mediante `.gitignore`.

## Tecnologías Utilizadas
* **Backend:** Python 3, Django 4.2
* **Frontend:** HTML5 Semántico, Bootstrap 5, JavaScript (Vanilla & Select2)
* **Arquitectura:** MVT (Model-View-Template)
* **Control de Versiones:** Git & GitHub (GitHub Flow)