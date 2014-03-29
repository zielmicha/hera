import os
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# use RSA private key sha512 digest
SECRET_KEY = hashlib.sha512(open(os.path.expanduser('~/.ssh/id_rsa')).read()).hexdigest()

INSTALLED_APPS = (
    'south',
    'hera',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data.db'),
    }
}
