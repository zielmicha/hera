from bottle import default_app
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
import hera.models
import json

def make():
    app = default_app.pop()
    app.catchall = False

    def error_catcher(environ, start_response):
        try:
            return app.wsgi(environ, start_response)
        except PermissionDenied:
            start_response('403 Permission denied', {})
            return [json.dumps({'status': 'PermissionDenied'}).encode()]
        except ObjectDoesNotExist as err:
            error = DoesNotExist_to_str(err)
            start_response('404 %s' % error, {}) # or 200?
            return [json.dumps({'status': error}).encode()]

    return error_catcher

def DoesNotExist_to_str(err):
    # convert DoesNotExist exception to more descriptive string
    # (by comparing DoesNotExist exception with all DoesNotExist exceptions in hera.models)
    for model in hera.models.__dict__.values():
        exc = getattr(model, 'DoesNotExist', None)
        if exc:
            if type(err) == exc:
                return '%sDoesNotExist' % model.__name__
    return type(err).__name__
