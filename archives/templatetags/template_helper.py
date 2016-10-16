from django import template
from django.conf import settings
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from archives.models import LEVEL_STATUS_CHOICES

register = template.Library()


@register.filter(name="whitehat_tag", need_autoescape=True)
def whitehat_level_tag_filter(name, autoescape=True):
    colors = dict((_[1][1], _[2]) for _ in settings.USER_LEVEL_RANGE)
    if autoescape:
        name = conditional_escape(name)
    return mark_safe('<span class="am-badge am-badge-{color}">{value}</span>'.format(color=colors[name], value=name))


@register.filter(name="post_tag", need_autoescape=True)
def post_level_tag_filter(value, autoescape=True):
    levels = (_[1] for _ in LEVEL_STATUS_CHOICES)
    colors = dict(zip(levels, ('secondary', 'primary', 'warning', 'danger')))

    if autoescape:
        value = conditional_escape(value)
    return mark_safe('<span class="am-badge am-badge-{color}">{value}</span>'.format(color=colors[value], value=value))


@register.filter(name="post_tag_color", is_safe=True)
def post_level_tag_color_filter(value):
    levels = (_[0] for _ in LEVEL_STATUS_CHOICES)
    colors = dict(zip(levels, ('secondary', 'primary', 'warning', 'danger')))

    return colors[value]


@register.filter(name="css", is_safe=True)
def css_filter(form, css):
    if 'class' in form.field.widget.attrs:
        form.field.widget.attrs['class'] += " %s" % css
    else:
        form.field.widget.attrs['class'] = css

    return form


@register.filter(name="placeholder", is_safe=True)
def placeholder_filter(form, default=""):
    text = default if default else form.label
    if 'placeholder' not in form.field.widget.attrs:
        form.field.widget.attrs['placeholder'] = text

    return form


@register.filter(name="first_error", is_safe=True)
def first_error_filter(errors):
    if not errors:
        return errors

    if 'captcha' in errors:
        data = errors['captcha'].as_text()
    else:
        data = errors.get(tuple(errors)[0]).as_text()

    return data


@register.filter
def level_progress_bar(rank):
    total = rank
    for index, level in enumerate(settings.USER_LEVEL_RANGE):
        if level[0][0] <= rank < level[0][1] and index < len(settings.USER_LEVEL_RANGE) - 1:
            total = level[0][1]
            break

    return rank / total * 100