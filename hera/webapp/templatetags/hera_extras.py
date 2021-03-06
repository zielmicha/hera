from django import template
from django.utils import html
import datetime
import babel.dates
import json

register = template.Library()

@register.filter
def money_format(value):
    minus_style = 'display: inline-block; width: 10px'
    minus = html.format_html('<span style="{0}">{1}</span>', minus_style,
                             '-' if value < 0 else ' ')
    as_string = '%.10f' % abs(value)
    whole, _, after_dot = as_string.partition('.')
    cents = after_dot[:2]
    rest = after_dot[2:6]
    result = html.format_html('{0}${1}.{2} {3}', minus, whole, cents, rest)
    if value < 0:
        result = html.format_html('<span class=minus-balance>{}</span>', result)
    return result

@register.filter
def pretty_delta(value):
    if isinstance(value, datetime.timedelta):
        delta = value
    else:
        delta = value - datetime.datetime.now()
    return babel.dates.format_timedelta(delta, locale='en_US')

@register.filter
def vm_uuid(value):
    if value == 'undefined':
        return 'initializing...'
    else:
        return html.format_html('<a href="/sandbox/{0}/" class=vm-uuid>{0}</a>', value)

@register.filter
def res_vm_uuid(res):
    delta = datetime.datetime.now() - res.expiry
    uuid = res.user_id
    if uuid == 'undefined' and delta > datetime.timedelta(seconds=5):
        return 'initialization failed'
    else:
        return vm_uuid(uuid)

@register.filter
def parse_json(value):
    return json.loads(value).items()
