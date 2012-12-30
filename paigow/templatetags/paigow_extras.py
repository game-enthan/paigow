from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from paigow.pghand import PGHand

from paigow.session_utils import session_player

register = template.Library()

# convenience functions for retrieving stuff from the request context.
def tile_size( context ):
  return context['pgtile_size']

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
    return opponent
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

@register.inclusion_tag( "pgdeal.html", takes_context=True )
def show_deal( context, pgsets, deal_owner ):
  # we might be showing the player, or we might be showing
  # the oppponent.  We pass this information on down.
  player_type = "player"
  player = session_player( context['request'] )  
  if ( deal_owner != player ):
    player_type = "opponent"
    context['is_opponent'] = True
  
  # this is the status of the player ("setting tiles" etc)
  context['player_state'] = context['game'].state_for_player( deal_owner )

  # this is called for both the player and the opponent, and will
  # show or hide the tiles and commands depending.
  context['deal_owner'] = deal_owner
  context['pgsets'] = pgsets
  context['player_type'] = player_type
  return context

@register.inclusion_tag( "switch_button.html", takes_context=True )
def show_switch_button( context, pgset_id ):
  # TBD: use other tag and render_to_template (or whatever it was)
  # so we can return nothing at all for opponent.
  context['pgset_id'] = pgset_id
  context['is_opponent'] = context['player_type'] == "opponent"
  return context
  #return { 'pgset_id': pgset_id, 'pgtile_size': tile_size( context ) }

@register.inclusion_tag( "pgset.html", takes_context=True )
def show_pgset( context, pgset, pgset_id, opponent ):
  #context['opponent'] = opponent
  context['pgset_id'] = pgset_id
  context['pgset'] = pgset
  return context

@register.inclusion_tag( "pgtile.html", takes_context=True )
def tile_image( context, tile, opponent ):
  if ( context['player_type'] == "opponent" ):
    context['pgtile'] = None
    context['background_position_css_value'] = "0px 0px"
  else:
    context['pgtile'] = tile
    context['background_position_css_value'] = tile.background_position_css_value( context['pgtile_size'] )
  return context

@register.simple_tag( takes_context=True )
def show_hand_label( context, tile1, tile2 ):
  if ( context['player_type'] == "opponent" ):
    return ""
  pghand = PGHand.create( tile1, tile2 )
  return pghand.label()
