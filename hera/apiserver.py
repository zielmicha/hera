from hera import api
from hera import apimiddleware

import bottle
import base64

from django.core.exceptions import PermissionDenied
from bottle import request, response, default_app

default_app.push()

@bottle.post('/sandbox/')
def create_sandbox():
    return get_session().create_sandbox(
        owner=request.forms['owner'],
        memory=int(request.forms['memory']),
        timeout=float(request.forms['timeout']),
        disk=request.forms['disk'],
    )

@bottle.post('/sandbox/:id/:action')
def sandbox_action(id, action):
    return get_session().sandbox_action(
        id, action, request.forms)

def get_session():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Basic '):
        response.status = 401
        response.set_header('WWW-Authenticate', 'Basic realm="use API key as password"')
        raise PermissionDenied() # TODO: do something more friendly than crashing
    user_pass = base64.b64decode(auth.split(' ')[1])
    account, _, api_key = user_pass.partition(b':')
    return api.Session(account, api_key)

app = apimiddleware.make()

if __name__ == '__main__':
    bottle.run(app=app, host='localhost', port=8080, server='cherrypy')
