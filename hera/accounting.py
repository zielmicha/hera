from hera import models

def add_derivative_resource(owner, values, timeout):
    res = models.DerivativeResource()
    # TODO: save etc
    return res

def add_resource_usage(owner, values, time):
    pass

def derivative_resource_used(id, user_type, user_id):
    pass

def derivative_resource_closed(id):
    pass

prize_per_mb = 4e-9

def compute_stats_prize(stats):
    return stats['memory'] * prize_per_mb
