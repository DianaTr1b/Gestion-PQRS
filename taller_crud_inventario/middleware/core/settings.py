import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apps.inventario',
    'apps.mantenimiento',
    'apps.usuarios',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.usuarios.middleware.InactiveUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

def _leer_pem(nombre: str) -> str:
    ruta = BASE_DIR / nombre
    if not ruta.exists():
        raise RuntimeError(f'Falta la llave JWT: {ruta}')
    return ruta.read_text()

GESTION_HUMANA_URL = env("GESTION_HUMANA_URL")
GESTION_HUMANA_CLIENT_ID = env("GESTION_HUMANA_CLIENT_ID")
GESTION_HUMANA_CLIENT_SECRET = env("GESTION_HUMANA_CLIENT_SECRET")
GESTION_HUMANA_TIMEOUT = 10
GESTION_HUMANA_JWKS_URL = env("GESTION_HUMANA_JWKS_URL", default="http://127.0.0.1:8000/microservice/.well-known/jwks.json/")
GESTION_HUMANA_AUDIENCE = env("GESTION_HUMANA_AUDIENCE", default="ecl-apps")
GESTION_HUMANA_ISSUER = env("GESTION_HUMANA_ISSUER", default="https://talento.ecl.com.co/microservice/")
GESTION_HUMANA_PUBLIC_KEY = _leer_pem('jwt-public.pem')

AUTHENTICATION_BACKENDS = [
    'apps.usuarios.authentication.JWTBackend',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': env.db()
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

_PROJECT_PREFIX = 'inventario'

# Cookies únicas (NO CAMBIAR, solo cambia el _PROJECT_PREFIX arriba)
SESSION_COOKIE_NAME = f'{_PROJECT_PREFIX}_sessionid'
CSRF_COOKIE_NAME = f'{_PROJECT_PREFIX}_csrftoken'

# Path de cookies
SESSION_COOKIE_PATH = '/'  # Usar '/' en localhost con puertos diferentes
CSRF_COOKIE_PATH = '/'     # Cambiar si usas subpaths en producción

# Seguridad
SESSION_COOKIE_HTTPONLY = True   # No accesible desde JavaScript
CSRF_COOKIE_HTTPONLY = False     # Necesita ser accesible para forms
SESSION_COOKIE_SECURE = not DEBUG  # Solo HTTPS en producción
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF
CSRF_COOKIE_SAMESITE = 'Lax'

# Expiración
SESSION_COOKIE_AGE = 43200  # 12 horas
SESSION_SAVE_EVERY_REQUEST = True  # Renueva sesión en cada request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Persiste al cerrar tabs

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/inventario/'
LOGOUT_REDIRECT_URL = '/login/'

# ==================== CONFIGURACIÓN DE EMAIL ====================

if DEBUG:
    
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=f'Sistema de Inventario <{EMAIL_HOST_USER}>')
SERVER_EMAIL = EMAIL_HOST_USER

# URL base del sistema para los links en los correos
BASE_URL = env('BASE_URL', default='http://127.0.0.1:8000')