from django import template
from django.utils import html
import datetime
import babel.dates

register = template.Library()

@register.filter
def money_format(value):
    minus_style = 'display: inline-block; width: 10px'
    minus = html.format_html('<span style="{0}">{1}</span>', minus_style,
                             '-' if value < 0 else ' ')
    as_string = str(abs(value))
    whole, after_dot = as_string.split('.')
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
    return html.format_html('<a href="/sandbox/{0}" class=vm-uuid>{0}</a>', value)
