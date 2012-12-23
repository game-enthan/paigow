from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from paigow.pghand import PGHand

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
  return "unknown"

@register.filter(needs_autoescape=True)
def state_for_player( value, arg, autoescape = None ):
  player = arg
  game = value
  return game.state_for_player( player )

@register.filter(needs_autoescape=True)
def state_for_opponent( value, arg, autoescape = None ):
  player = arg
  game = value
  opponents = player.opponents_for_game( game )
  if ( opponents ):
    opponent = opponents[0]
    return game.state_for_player( opponent )
  else:
    return "unknown state"

@register.inclusion_tag("pgtile.html", takes_context=True)
def tile_image( context, tile, tile_size ):
  return { 'pgtile': tile, 'pgtile_size': tile_size }

@register.inclusion_tag("pghand.html", takes_context=True)
def show_hand( context, pgset_id, pgtile1, pgtile2, pgtile_size ):
  return { 'pgset_id': pgset_id, 'pgtile1': pgtile1, 'pgtile2': pgtile2, 'pgtile_size': pgtile_size }

@register.inclusion_tag("pgset.html", takes_context=True)
def show_pgset( context, pgset, pgset_id, tile_size ):
  return { 'pgset': pgset, 'pgset_id': pgset_id, 'pgtile_size': tile_size }

@register.inclusion_tag("switch_button.html", takes_context=True)
def show_switch_button( context, pgset_id, tile_size ):
  return { 'pgset_id': pgset_id, 'pgtile_size': tile_size }

@register.simple_tag(takes_context=True)
def show_hand_label( context, tile1, tile2 ):
  pghand = PGHand.create( tile1, tile2 )
  return pghand.label()
