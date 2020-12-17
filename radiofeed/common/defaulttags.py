# Django
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

# Local
from .html import clean_html_content, stripentities

register = template.Library()


@register.filter
@stringfilter
def clean_html(value):
    return mark_safe(stripentities(clean_html_content(value)))


@register.filter
def subtract(value_a, value_b):
    return value_a - value_b