from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(needs_autoescape=True)
def tile_html_string(value,autoescape=None):
  return mark_safe(value.html_image())

