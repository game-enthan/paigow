from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from mainsite.settings import STATIC_URL
from paigow.models.pgtile import TILE_IMAGE_WIDTH, TILE_IMAGE_HEIGHT

register = template.Library()

@register.simple_tag
def title():
  return "Pai Gow"

@register.filter(needs_autoescape=True)
def opponent_for_game( value, arg, autoescape = None ):
  player = arg
  game = value
  opponents = player.opponents_for_game( game )
  if ( opponents ):
    opponent = opponents[0]
    return mark_safe( opponent.name )
  return "computer"

@register.inclusion_tag("tile.html", takes_context=True)
def tile_image( context, tile, tile_style ):
  return { 'tile': tile, 'tile_style': tile_style }

