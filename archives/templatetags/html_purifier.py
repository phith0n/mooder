from django import template
from mooder.extends.purifier import XssHtml

register = template.Library()


@register.filter(name="purifier", is_safe=True)
def html_purifier_filter(value):
    parser = XssHtml()
    parser.feed(value)
    parser.close()
    return parser.getHtml()