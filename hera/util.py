import datetime

epoch = datetime.datetime.utcfromtimestamp(0)

def datetime_to_unix(dt):
    return (dt - epoch).total_seconds()

def do_nothing(*args, **kwargs):
    pass

def is_true(v):
    return v is not None and v.lower() in ('1', 'true', 't', 'yes', 'y')
