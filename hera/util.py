
def do_nothing(*args, **kwargs):
    pass

def is_true(v):
    return v.lower() in ('1', 'true', 't', 'yes', 'y')
