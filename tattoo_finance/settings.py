import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de um .env local, se existir (em produção use as
# variáveis de ambiente da plataforma).
load_dotenv(BASE_DIR / '.env')

# Detecta se está rodando no Render (a plataforma define RENDER=true).
ON_RENDER = bool(os.environ.get('RENDER'))

# DEBUG: desligado por padrão no Render; ligado localmente.
# Pode ser forçado com a variável DJANGO_DEBUG.
_default_debug = 'False' if ON_RENDER else 'True'
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
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Inclui automaticamente o domínio público atual do Render.
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')

# Hosts extras via env (ex.: domínio personalizado), separados por vírgula.
_extra_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
for _host in (h.strip() for h in _extra_hosts.split(',')):
    if _host and _host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_host)
        CSRF_TRUSTED_ORIGINS.append(f'https://{_host}')

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
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

# Banco de dados. Ordem de preferência:
#   1. DATABASE_URL — fornecida pelo Render ao vincular um Postgres.
#   2. Variáveis MYSQL_* — compatibilidade com setups MySQL existentes.
#   3. SQLite local — apenas desenvolvimento.
def _mysql_env(*names, default=''):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default

_database_url = os.environ.get('DATABASE_URL')
_mysql_db = _mysql_env('MYSQL_DATABASE', 'MYSQLDATABASE')

if _database_url:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif _mysql_db:
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
elif ON_RENDER:
    # No Render o disco é efêmero: cair silenciosamente no SQLite significa
    # perder todos os dados no próximo deploy. Melhor falhar com erro claro.
    raise ImproperlyConfigured(
        'DATABASE_URL não encontrada no Render. Vincule um banco Postgres ao '
        'serviço (ou defina as variáveis MYSQL_*) antes de fazer o deploy.'
    )
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
