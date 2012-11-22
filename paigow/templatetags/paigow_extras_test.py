from django import template

register = template.Library()

@register.simple_tag
def foobar():
  return ("A", "B")
foobar = register.simple_tag(foobar)
