from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from mainsite.settings import STATIC_URL
from paigow.models.pgtile import TILE_IMAGE_WIDTH, TILE_IMAGE_HEIGHT

register = template.Library()

@register.simple_tag
def title():
  return "Pai Gow"

# Filter a tile and put this string inside an IMG object to get a tile image:
#
#        <img {{ tile|tile_html_string }}></img>.
#
# This will result in a 1x1 transparent GIF, scaled to the size of the tile
# 
@register.filter(needs_autoescape=True)
def tile_html_string(value,autoescape=None):
  out_str = " style=\""
  out_str += "display:block;background-image:url('" + STATIC_URL + "tiles.jpg');"
  out_str += "background-repeat:no-repeat;"
  out_str += "width:" + TILE_IMAGE_WIDTH + "px;height:" + TILE_IMAGE_HEIGHT + "px;"
  out_str += "background-position:-" + str(value.sprite_left) + "px -" + str(value.sprite_top) + "px;\""
  out_str += "src=\"" + STATIC_URL + "img_trans.gif\""
  out_str += "width=" + TILE_IMAGE_WIDTH + " height=" + TILE_IMAGE_HEIGHT
  return mark_safe(out_str)


@register.filter(needs_autoescape=True)
def opponent_for_game( value, arg, autoescape = None ):
  player = arg
  game = value
  opponents = player.opponents_in_game( game )
  if ( opponents ):
    opponent = opponents[0]
    return mark_safe( opponent.name )
  return "computer"
