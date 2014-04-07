import os
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# use RSA private key sha512 digest
SECRET_KEY = hashlib.sha512(open(os.path.expanduser('~/.ssh/id_rsa'), 'rb').read()).hexdigest()

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
    'hera',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data.db'),
    }
}

STATIC_URL = '/static/'

IMAGE_STORAGE = BASE_DIR + '/images'
DISPATCHER_HTTP = 'http://localhost:10002/'
DISPATCHER_SOCKET = ('localhost', 10001)

DEBUG = False

ROOT_URLCONF = 'hera.urls'

exec(open(BASE_DIR + '/hera/local_settings.py').read())
