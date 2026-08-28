import jwt
import logging
import requests
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()

logger = logging.getLogger(__name__)


class JWTBackend(BaseBackend):
    """
    Autenticación centralizada vía JWT emitido por gestión humana (idp)

    - Modo login (password): valida credenciales contra RH y verifica el access token localmente con la clave pública
    """

    def authenticate(self, request, username = None, password = None, token = None):
        if token:
            return self._user_desde_token(token)

        if not username or not password:
            return None

        try:
            response = requests.post(
                f"{settings.GESTION_HUMANA_URL}/microservice/api-auth/login/",
                json={'username': username, 'password': password},
                timeout=settings.GESTION_HUMANA_TIMEOUT
            )
        except requests.RequestException:
            return None

        if response.status_code != 200:
            return None

        data = response.json()
        access = data.get("access")
        if not access:
            return None

        user = self._user_desde_token(access)
        if user is not None:
            user._gh_data = data.get("user", {})
            user._gh_data_access = access
        return user

    def _user_desde_token(self, token):
        """
        Verifica el JWT y busca/crea el PerfilUsuario local
        
        Reglas:
        - Solo acepta access token (nunca refresh)
        - La identidad cánonica es uuid_gh (el claim 'sub')
        - En el login no se sobreescriben first_name/last_name/email/is_active estos datos solo cambian
        por webhook/pull (eventos controlados).
        - La desactivación en GH solo propaga vía webhook; un jwt nunca reactiva.
        """
        from .models import PerfilUsuario

        try:
            payload = jwt.decode(
                token,
                settings.GESTION_HUMANA_PUBLIC_KEY,
                algorithms=['RS256'],
                audience=settings.GESTION_HUMANA_AUDIENCE,
                issuer=settings.GESTION_HUMANA_ISSUER
            )
        except jwt.PyJWTError as exc:
            logger.warning(f"JWT inválido: {exc}")
            return None

        if payload.get("token_type") != "access":
            logger.warning("Token rechazado: token_type=%s", payload.get("token_type"))
            return None

        sub = payload.get("sub")
        user_id = payload.get("user_id")
        if not sub:
            return None

        # GH ya denegó el login si la identidad está inactiva; esto es solo
        # defensa en profundidad por si llega un token emitido antes de la baja.
        if not payload.get("is_active", True):
            logger.info("Acceso denegado: identidad inactiva en Talento (sub=%s)", sub)
            return None

        # Buscar por clave cánonica (uuid/sub) con fallback a la clave legacy
        # (id de GH) para reconciliar los duplicados históricos.
        perfil = (
            PerfilUsuario.objects.select_related('user')
            .filter(Q(uuid_gh=sub)|Q(gestion_humana_id=user_id))
            .first()
        )

        if perfil:
            user = perfil.user
            # Backfill de la clave cánonica si el perfil venía del webhook/pull.
            if not perfil.uuid_gh:
                perfil.uuid_gh = sub
                perfil.save(update_fields=['uuid_gh'])
            # Sin escrituras de datos: los nombres/emails/is_active son de GH
            # y solo cambian por webhook. El estado local lo decide Inventario
            return user

        # Primer acceso: provisionar (una sola vez)
        username_base = payload.get("username") or f"gh_{sub[:8]}"
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=payload.get("email") or "",
            first_name=payload.get("given_name") or "",
            last_name=payload.get("family_name") or "",
        )

        user.set_unusable_password()
        user.save()

        PerfilUsuario.objects.create(
            user=user,
            uuid_gh=sub,
            gestion_humana_id=user_id,
            ultima_sincronizacion_gh=timezone.now()
        )
        return user


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None