from bottle import default_app
from django.core.exceptions import PermissionDenied
import json

def make():
    app = default_app.pop()
    app.catchall = False

    def error_catcher(environ, start_response):
        # maybe better to fake the start_response callable but this work
        try:
            return app.wsgi(environ, start_response)
        except PermissionDenied:
            start_response('403 Permission denied', {})
            return [json.dumps({'status': 'PermissionDenied'})]

    return error_catcher
