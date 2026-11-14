"""Django settings for the local VoxCentraAI project.

Production values that contain secrets or deployment details come from the
process environment. Local development uses an ephemeral signing key if none is
provided, so no production secret is committed to source code.
"""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from django.utils.csp import CSP
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name, default=()):
    value = os.environ.get(name)
    if value is None:
        return list(default)
    values = [item.strip() for item in value.split(",") if item.strip()]
    if "*" in values:
        raise ImproperlyConfigured(f"{name} must not contain a wildcard host.")
    return values


ENVIRONMENT = os.environ.get("DJANGO_ENV", "development").strip().lower()
IS_PRODUCTION = ENVIRONMENT == "production"
if ENVIRONMENT not in {"development", "local", "test", "production"}:
    raise ImproperlyConfigured("DJANGO_ENV must be development, local, test, or production.")

_configured_secret_key = os.environ.get("DJANGO_SECRET_KEY", "").strip()
if IS_PRODUCTION and len(_configured_secret_key) < 50:
    raise ImproperlyConfigured(
        "Production requires DJANGO_SECRET_KEY with at least 50 characters generated securely."
    )
SECRET_KEY = _configured_secret_key or get_random_secret_key()
DEBUG = _env_bool("DJANGO_DEBUG", False) and not IS_PRODUCTION

if IS_PRODUCTION:
    ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS")
    if not ALLOWED_HOSTS:
        raise ImproperlyConfigured("Production requires explicit DJANGO_ALLOWED_HOSTS.")
else:
    ALLOWED_HOSTS = _env_list(
        "DJANGO_ALLOWED_HOSTS", ("localhost", "127.0.0.1", "::1")
    )

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "comercios.apps.ComerciosConfig",
    "accesos.apps.AccesosConfig",
    "catalogo.apps.CatalogoConfig",
    "clientes.apps.ClientesConfig",
    "interacciones.apps.InteraccionesConfig",
    "pedidos.apps.PedidosConfig",
    "cuentas.apps.CuentasConfig",
    "axes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "voxcentra.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.csp",
            ],
        },
    },
]

ASGI_APPLICATION = "voxcentra.asgi.application"
WSGI_APPLICATION = "voxcentra.wsgi.application"

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

_db_name = os.environ.get("DJANGO_DB_NAME", "").strip()
_db_path = Path(_db_name) if _db_name else BASE_DIR / "db.sqlite3"
if not _db_path.is_absolute():
    _db_path = BASE_DIR / _db_path

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _db_path,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 15},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_USE_ATTEMPT_EXPIRATION = True
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_RETRY_AFTER_HEADER = True
AXES_SENSITIVE_PARAMETERS = ["username", "password", "ip_address", "password1", "password2"]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "cuentas:login"
LOGIN_REDIRECT_URL = "cuentas:dashboard"
LOGOUT_REDIRECT_URL = "cuentas:login"

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 8 * 60 * 60
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = _env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

LOCAL_PORT = int(os.environ.get("DJANGO_LOCAL_PORT", "8000"))

SECURE_CSP = {
    "default-src": [CSP.SELF],
    "base-uri": [CSP.SELF],
    "connect-src": [CSP.SELF, f"ws://127.0.0.1:{LOCAL_PORT}", f"ws://localhost:{LOCAL_PORT}"],
    "font-src": [CSP.SELF],
    "form-action": [CSP.SELF],
    "frame-ancestors": [CSP.NONE],
    "img-src": [CSP.SELF],
    "media-src": [CSP.SELF],
    "object-src": [CSP.NONE],
    "script-src": [CSP.SELF, CSP.NONCE],
    "style-src": [CSP.SELF, CSP.NONCE],
}

if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31_536_000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

if IS_PRODUCTION:
    email_host = os.environ.get("DJANGO_EMAIL_HOST", "").strip()
    if not email_host:
        raise ImproperlyConfigured("Production requires DJANGO_EMAIL_HOST for SMTP email.")
    email_use_tls = _env_bool("DJANGO_EMAIL_USE_TLS", True)
    email_use_ssl = _env_bool("DJANGO_EMAIL_USE_SSL", False)
    if email_use_tls and email_use_ssl:
        raise ImproperlyConfigured("Configure only one of DJANGO_EMAIL_USE_TLS or DJANGO_EMAIL_USE_SSL.")
    DEFAULT_FROM_EMAIL = os.environ.get("DJANGO_DEFAULT_FROM_EMAIL", "webmaster@localhost")
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "OPTIONS": {
                "host": email_host,
                "port": int(os.environ.get("DJANGO_EMAIL_PORT", "587")),
                "username": os.environ.get("DJANGO_EMAIL_USER", ""),
                "password": os.environ.get("DJANGO_EMAIL_PASSWORD", ""),
                "use_tls": email_use_tls,
                "use_ssl": email_use_ssl,
                "timeout": 10,
            },
        },
    }
else:
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.console.EmailBackend",
        },
    }
