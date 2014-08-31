import os
import sys
import shutil
import subprocess
import pwd
import grp

from django.conf import settings
dir = os.path.abspath(os.path.dirname(sys.argv[0]))
settings.configure(TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
), TEMPLATE_DIRS=(dir, ))
from django.template.loader import render_to_string

sys.path.append(dir + '/..')
from hera import settings

def is_sudoer():
    try:
        return grp.getgrnam('sudo').gr_gid in os.getgroups()
    except KeyError:
        return False

as_root = is_sudoer()
conf = dict(
    port=80 if as_root else 9000,
    suffix='hera.dev',
    servers=[
        dict(name='www', servers={'/': 'localhost:8001'}),
        dict(name='api', servers={'/': 'localhost:8080'}),
        dict(name='proxy', servers={'/': '%s:%d' % settings.PROXY_HTTP_ADDR,
                                    '/ws/': '%s:%d' % settings.PROXY_WS_ADDR}),
    ],
    user=pwd.getpwuid(os.getuid()).pw_name if as_root else None,
)

print('Running nginx at port %d' % conf['port'])
print('Expecting hostnames:')
for name in set( serv['name'] for serv in conf['servers'] ):
    print('- %s.%s' % (name, conf['suffix']))

def mkdir(name):
    if not os.path.isdir(name):
        os.mkdir(name)

os.chdir(dir)
mkdir('nginx_data')
mkdir('nginx_data/conf')
mkdir('nginx_data/logs')

config = render_to_string('nginx_nginx.conf', conf)
with open('nginx_data/conf/nginx.conf', 'w') as f:
    f.write(config)

shutil.copyfile('nginx_mime.types', 'nginx_data/conf/mime.types')

prefix = ['sudo'] if as_root else []
try:
    subprocess.check_call(prefix + ['../deps/nginx/objs/nginx',
                                    '-p', dir + '/nginx_data'])
except Exception as err:
    print('nginx returned error', err)
    sys.exit(1)
