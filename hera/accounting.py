from hera import models

def add_derivative_resource(owner, values, timeout):
    res = models.DerivativeResource()
    res.owner = models.Owner.objects.get(name=owner)
    res.timeout = timeout
    res.save()

def add_resource_usage(owner, values, time):
    pass

def derivative_resource_used(id, user_type, user_id):
    pass
