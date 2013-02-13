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

@register.inclusion_tag( "opponent_summary.html", takes_context=True )
def show_opponent_summary( context, opponent ):
  player = session_player( context['request'] )  
  context['opponent'] = opponent
  context['games'] = player.games_against_opponent( opponent )
  wins, losses, in_progress = player.record_against_opponent( opponent )
  context['record_against_opponent'] = str( wins ) + " - " + str( losses )
  return context

@register.inclusion_tag( "game_summary.html", takes_context=True )
def show_game_summary( context, game ):
  from paigow.models.pggame import PGGame
  player = session_player( context['request'] )  
  opponent = player.opponent_for_game( game )
  context['game'] = game
  context['opponent'] = opponent
  player_score = game.score_for_player( player )
  opponent_score = game.score_for_player( opponent )
  context['score'] = str(player_score) + " - " + str(opponent_score)
  if game.game_state != PGGame.GAME_OVER:
    context['score_class'] = "score-in-progress"
  elif player_score > opponent_score:
    context['score_class'] = "score-win"
  else:
    context['score_class'] = "score-lose"
  return context

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
  context['player_state'] = context['game'].state_for_player( deal_owner, context['deal_number'] )

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
    # context['background_position_css_value'] = "0px 0px"
    context['dots'] = []
  else:
    from paigow.pgdot import PGDot
    context['pgtile'] = tile
    # context['background_position_css_value'] = tile.background_position_css_value( context['pgtile_size'] )
    context['dots'] = PGDot.all_dots( tile.dot_sequence )
  return context

@register.simple_tag( takes_context=True )
def show_hand_label( context, tile1, tile2 ):
  if ( context['player_type'] == "opponent" ):
    return "--"
  pghand = PGHand.create( tile1, tile2 )
  return pghand.label()
