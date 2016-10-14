from django import template
from mooder.settings import USER_LEVEL_RANGE
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from archives.models import LEVEL_STATUS_CHOICES

register = template.Library()


@register.filter(name="whitehat_tag", need_autoescape=True)
def whitehat_level_tag_filter(name, autoescape=True):
    colors = dict((_[1][1], _[2]) for _ in USER_LEVEL_RANGE)
    if autoescape:
        name = conditional_escape(name)
    return mark_safe('<span class="label label-{color}">{value}</span>'.format(color=colors[name], value=name))


@register.filter(name="post_tag", need_autoescape=True)
def post_level_tag_filter(value, autoescape=True):
    levels = (_[1] for _ in LEVEL_STATUS_CHOICES)
    colors = dict(zip(levels, ('secondary', 'primary', 'warning', 'danger')))

    if autoescape:
        value = conditional_escape(value)
    return mark_safe('<span class="label label-{color}">{value}</span>'.format(color=colors[value], value=value))


@register.filter
def absolute(value):
    """
    Get the absolute value for "value".  This template tag is a wrapper for
    pythons "abs(...)" method.

    Usage:

    >>> absolute(-5)
    5
    """
    try:
        return abs(value)
    except:
        return value