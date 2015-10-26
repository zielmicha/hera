import logging
import datetime

from hera import models
from django.db.models import F
from django.db import transaction

logger = logging.getLogger('accounting')

resource_timeouts = {
    'vm': 4.0,
}

def add_derivative_resource(owner,
                            user_type,
                            user_id,
                            base_price_per_second=0.0):
    logger.info('add owner=%s user=(%s, %s)', owner, user_type, user_id)
    max_time_left = resource_timeouts[user_type]
    owner = models.Account.objects.get(name=owner)
    res = models.DerivativeResource(owner=owner,
                                    user_type=user_type,
                                    user_id=user_id,
                                    base_price_per_second=base_price_per_second,
                                    expiry=datetime.datetime.now()
                                    + datetime.timedelta(seconds=max_time_left))
    return res

def add_derivative_vm_resource(owner, values):
    price = compute_stats_price(values)
    res = add_derivative_resource(owner,
                                  user_type='vm',
                                  user_id='undefined',
                                  base_price_per_second=price)
    res.save()
    return res

@transaction.atomic
def derivative_resource_used(id, user_type, user_id):
    logger.info('use %s user=(%s, %s)', id, user_type, user_id)
    res = models.DerivativeResource.objects.get(id=id)
    if res.user_type != user_type:
        raise ValueError('adding usage %r to resource %r' % (user_type, res.user_type))
    old_user_id = res.user_id
    if old_user_id != user_id:
        res.user_id = user_id
        res.save()

    # if old_user_id != 'undefined':
    #    raise ValueError('tried to change resource user_id to %r from %r' % (user_id, old_user_id))

    if res.closed_at:
        raise ValueError('attempted to use closed resource')

    last = None

    try:
        last = models.DerivativeResourceUsed.objects\
                                            .filter(resource=res)\
                                            .order_by('-end_time')[0:1]\
                                            .get()
    except models.DerivativeResourceUsed.DoesNotExist:
        last_time = datetime.datetime.now()
    else:
        last_time = last.end_time

    now = datetime.datetime.now()
    real_time_left = (now - last_time).total_seconds()
    max_time_left = resource_timeouts[user_type]

    time_left = min(max_time_left, real_time_left)

    price = float(res.base_price_per_second) * time_left

    if not last or real_time_left > max_time_left:
        models.DerivativeResourceUsed(resource=res,
                                      start_time=last_time,
                                      end_time=now,
                                      price=price).save()
    else:
        models.DerivativeResourceUsed.objects.filter(pk=last.pk).update(
            end_time=now, price=F('price') + price)

    models.DerivativeResource.objects.filter(pk=res.pk).update(
        expiry=now + datetime.timedelta(seconds=max_time_left))
    models.Account.objects.filter(pk=res.owner.pk).update(
        price_used=F('price_used') + price)

def derivative_resource_closed(id):
    logger.info('close %s', id)
    res = models.DerivativeResource.objects.get(id=id)
    res.close()

price_per_mb = 4e-9

def compute_stats_price(stats):
    return stats['memory'] * price_per_mb
