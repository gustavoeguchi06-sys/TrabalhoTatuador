import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de um .env local, se existir (em produção use as
# variáveis de ambiente da plataforma).
load_dotenv(BASE_DIR / '.env')

# Detecta se está rodando no Railway (a plataforma define essa variável).
ON_RAILWAY = bool(os.environ.get('RAILWAY_ENVIRONMENT'))

# DEBUG: desligado por padrão no Railway; ligado localmente.
# Pode ser forçado com a variável DJANGO_DEBUG.
_default_debug = 'False' if ON_RAILWAY else 'True'
DEBUG = os.environ.get('DJANGO_DEBUG', _default_debug).lower() in ('1', 'true', 'yes')

# SECURITY
# Em produção a SECRET_KEY precisa vir do ambiente; sem ela o deploy falha
# em vez de rodar com uma chave pública e adivinhável.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'insecure-development-key'
    else:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY não definida. Configure a variável de ambiente '
            'com um valor secreto antes de rodar em produção.'
        )

ALLOWED_HOSTS = [
    "trabalhotatuador-production.up.railway.app",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://trabalhotatuador-production.up.railway.app",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Inclui automaticamente o domínio público atual do Railway.
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)
    CSRF_TRUSTED_ORIGINS.append(f'https://{_railway_domain}')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Endurecimento aplicado apenas em produção (DEBUG desligado).
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 dias
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'finance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Exige login em todas as views, exceto as marcadas com @login_not_required.
    'django.contrib.auth.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'finance:list'
LOGOUT_REDIRECT_URL = 'login'

ROOT_URLCONF = 'tattoo_finance.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tattoo_finance.wsgi.application'

# Aceita tanto MYSQL_DATABASE (manual) quanto MYSQLDATABASE (nome nativo do Railway).
def _mysql_env(*names, default=''):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default

_mysql_db = _mysql_env('MYSQL_DATABASE', 'MYSQLDATABASE')
if ON_RAILWAY and not _mysql_db:
    # No Railway o disco é efêmero: cair silenciosamente no SQLite significa
    # perder todos os dados no próximo deploy. Melhor falhar com erro claro.
    raise ImproperlyConfigured(
        'Variáveis do MySQL não encontradas no Railway (MYSQL_DATABASE/MYSQLDATABASE). '
        'Vincule o serviço MySQL ou defina as variáveis de conexão.'
    )
if _mysql_db:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': _mysql_db,
            'USER': _mysql_env('MYSQL_USER', 'MYSQLUSER', default='root'),
            'PASSWORD': _mysql_env('MYSQL_PASSWORD', 'MYSQLPASSWORD'),
            'HOST': _mysql_env('MYSQL_HOST', 'MYSQLHOST', default='127.0.0.1'),
            'PORT': _mysql_env('MYSQL_PORT', 'MYSQLPORT', default='3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Permite ao WhiteNoise servir direto de STATICFILES_DIRS,
# sem depender de collectstatic no build.
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
