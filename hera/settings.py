import os
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = None

# for admin;
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',

    'south',
    'registration',
    'hera',
    'hera.webapp',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data.db'),
    }
}

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "deps/bootstrap/dist"),
    os.path.join(BASE_DIR, "deps/bootswatch"),
    os.path.join(BASE_DIR, "deps/xterm.js/src"),
)

IMAGE_STORAGE = BASE_DIR + '/images'

DISPATCHER_SOCKET = ('localhost', 10001)
DISPATCHER_HTTP = 'http://localhost:10002/'

API_HTTP_ADDR = ('localhost', 8080)
API_HTTP = 'http://%s:%d/' % API_HTTP_ADDR

PROXY_RAW_ADDR = ('10.128.0.1', 10003)
PROXY_WS_ADDR = ('localhost', 10004)
PROXY_HTTP_ADDR = ('localhost', 10005)

PROXY_WS = 'ws://%s:%d/' % PROXY_WS_ADDR
PROXY_HTTP = 'http://%s:%d/' % PROXY_HTTP_ADDR

REDIS_ADDR = ('localhost', 6379)
REDIS_DB_BASE = 'hera_'
REDIS_PASSWORD = None

DEBUG = False

ROOT_URLCONF = 'hera.urls'

exec(open(BASE_DIR + '/local_settings.py').read())

if not SECRET_KEY:
    # use RSA private key sha512 digest
    SECRET_KEY = hashlib.sha512(open(os.path.expanduser('~/.ssh/id_rsa'), 'rb').read()).hexdigest()
