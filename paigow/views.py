# These are referenced from 'urls.py'

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotAllowed

from models.pgtile import PGTile
from paigow.pghand import PGHand
from models.pggame import PGGame
from models.pgplayer import PGPlayer
from paigow.pgset import PGSet

from paigow.session_utils import session_player


#-------------------------------------------------------------------
# convenience
# return the PGPlayer with the current request session id
def xsession_player( request ):
  if 'player_id' in request.session:
    return PGPlayer.with_id( request.session['player_id'] )
  else:
    return None

#-------------------------------------------------------------------
# convenience
# return the PGPlayer with the POSTed player ID value
def posted_player_from_id_field( request, field_name ):
  if field_name in request.POST:
    return PGPlayer.with_id( request.POST[field_name] )
  else:
    return None


#-------------------------------------------------------------------
# convenience
# final setup of the params with stuff common to all views
def request_context( request, params ):
  
  # protect against cross-site request forgery
  params.update( csrf( request ) )
  
  # set up the URLs for the app-wide menus
  params['logout_url'] = '/paigow/logout'
  params['home_url'] = '/paigow/home'
  
  params['activities'] = (
      { 'name': "Start New Game", 'url': '/paigow/game/new' }, )
  
  # setup players and possible opponents
  player = session_player( request )
  if ( not player ):
    request.session['player_id'] = None
    params['playername'] = None
    params['opponents'] = None
  else:
    params['playername'] = player.name
    params['opponents'] = player.all_possible_opponents()
  params['player'] = player

  return RequestContext( request, params )


#-------------------------------------------------------------------
# make sure we are redirected to the right place
def goto_home( request, params = {} ):
  return redirect( '/paigow/home', request, params )


#-------------------------------------------------------------------
# home page: if they're not logged in, allow them to log in or register.
# if they are logged in, show them the home page (TBD).
def home( request, params = {} ):
  
  if (not request.session.get('player_id', False)):
    return render_to_response( 'user_login.html', request_context( request, params ) )

  params['games'] = session_player( request ).games()
  return render_to_response( 'home.html', request_context( request, params ) )


#-------------------------------------------------------------------
# a player has registered or logged in: remember them in the session,
# and make sure to parse the 'remember_me' setting.
def add_player_to_session( request, player, checkbox_name_prefix ):
  
  # remember this player in the session
  request.session['player_id'] = player.id
  
  # if they haven't clicked 'remember me', make sure it expires.
  full_field_name = checkbox_name_prefix + '_remember_me'
  if not request.POST.get( full_field_name, False ):
    request.session.set_expiry(0)


#-------------------------------------------------------------------
# the user clicked the 'Register' button on the login page
def register( request, params = {} ):
  
  username = request.POST['register_username']
  email = request.POST['register_email']
  params = { 'username' : username, 'email' : email }
  
  # check for the parameters we need to register.
  is_good_so_far = True
  if ( not username ):
    messages.add_message(request, messages.ERROR, "A username is required to register.")
    is_good_so_far = False
  else:
    existing_player = PGPlayer.objects.filter( name = username )
    if ( existing_player ):
      messages.add_message(request, messages.ERROR, "There is already a player with that username.")
      is_good_so_far = False
  
  if ( not email ):
    messages.add_message(request, messages.ERROR, "Email is required to register.")
    is_good_so_far = False
  
  password = request.POST['register_password']
  if ( not password ):
    messages.add_message(request, messages.ERROR, "A password is required to register.")
    is_good_so_far = False
  
  # did it pass muster?
  if ( not is_good_so_far ):  
    return render_to_response( 'user_login.html', request_context( request, params ) )
  
  # we are good, add this to the players!
  player = PGPlayer.create( username, email, password )
  player.save()
  add_player_to_session( request, player, 'register' )
  messages.add_message(request, messages.INFO, username + " is now registered and logged in." )
  
  return goto_home( request, params )


#-------------------------------------------------------------------
# the user clicked the 'Register' button on the login page
def login( request, params = {} ):
  
  username = request.POST['login_username']
  if ( not username ):
    params['username'] = username
    messages.add_message(request, messages.ERROR, "Please provide a username.")
    return render_to_response( 'user_login.html', request_context( request, params ) )
  
  players = PGPlayer.objects.filter( name = username )
  if ( not players ):
    messages.add_message(request, messages.ERROR, "Your username and/or password didn't match.")
    params['username'] = username
    return render_to_response( 'user_login.html', request_context( request, params ) )
  
  password = request.POST['login_password']
  if password != request.POST['login_password']:
    messages.add_message(request, messages.ERROR, "Your username and/or password didn't match.")
    return render_to_response( 'user_login.html', request_context( request, params ) )
  
  add_player_to_session( request, players[0], 'login' )
  messages.add_message(request, messages.INFO, username + " is now logged in." )
  
  return goto_home ( request, params )


#-------------------------------------------------------------------
# The user chose 'Logout' from the user menu
def logout( request, params = {} ):
  
  request.session['player_id'] = None
  return goto_home ( request, params )


#-------------------------------------------------------------------
# User clicked 'New Game': return a form so they can create one.
def new_game( request, params = {} ):
  
  if (not request.session.get('player_id', False)):
    return goto_home( request )
  
  return render_to_response( 'game_create.html', request_context( request, params ) )


#-------------------------------------------------------------------
# User clicked 'Add Game' after filling in a game: add it and save it,
# and go home.
def add_game( request, params = {} ):
  
  if (not request.session.get('player_id', False)):
    return goto_home( request )

  # create a new game
  game = PGGame.create( request.POST['game_name'] )
  game.save() # must be done before adding player, so we have an ID
  
  # add ourselves and the opponent (which automatically saves)
  game.add_player( session_player( request ) )
  game.add_player( posted_player_from_id_field( request, 'game_opponent' ) )
  
  messages.add_message( request, messages.INFO, "Game \"" + game.name + "\" created." )
  
  return goto_home ( request, params )


#-------------------------------------------------------------------
# User clicked a URL that corresponds to a game.
def play_game( request, game_id, params = {} ):
  
  from models.pgtile import PGTile
  from pghand import PGHand
  from paigow.models import PGPlayerInGame
  
  player_id = request.session.get('player_id', False) 
  if ( not player_id ):
    return goto_home( request )
  player = PGPlayer.objects.get( id = player_id )
  
  # get the game from the db
  game = PGGame.with_id( game_id )
  if ( not game ):
    messages.add_message( request, messages.ERROR, "WTF?  That game has disappeared into the ether (which doesn't exist)" )
    return goto_home( request )
  
  # set the score for the other player.
  players_in_game = game.players()
  
  # make sure you're in the game: you can't look at other games.
  if not ( player in players_in_game ):
    messages.add_message( request, messages.ERROR, "I'm sorry, you are not allowed in that game, it's only for VIPs" )
    return goto_home( request )
  
  you_in_game = PGPlayerInGame.objects.filter( game = game, player = player )

  # set the game and score for you
  params['game'] = game
  params['score_you'] = you_in_game[0].score
  
  # set up the opponent for the template
  params['opponent'] = session_player( request ).opponents_for_game( game )[0]
  
  # get your opponent's score
  other_player_in_game = PGPlayerInGame.objects.filter( game = game, player = params['opponent'] )
  params['score_opponent'] = -1
  if ( other_player_in_game[0] ):
    params['score_opponent'] = other_player_in_game[0].score
  
  # deal if it's not already dealt
  if ( game.game_state == PGGame.ABOUT_TO_DEAL ):
    game.deal_tiles()
  
  # create the hands for this player
  params['pgsets'] = game.sets_for_player( session_player( request ) )
  params['pgtile_size'] = "medium"
  
  return render_to_response( 'game_play.html', request_context( request, params ) )


#-------------------------------------------------------------------
# AJAX response for the label for a hand
def data_hand_label( request, params = {} ):
  hand_chars = request.GET['hand']
  pghand = PGHand.create( PGTile.objects.get( tile_char = hand_chars[0] ), PGTile.objects.get( tile_char = hand_chars[1] ) )
  label = pghand.label()
  pghand = PGHand.create( PGTile.objects.get( tile_char = hand_chars[2] ), PGTile.objects.get( tile_char = hand_chars[3] ) )
  label = label + "|" + pghand.label()
  return HttpResponse( label )

#-------------------------------------------------------------------
# AJAX response for the opponent state
def data_opponent_state( request, game_id ):
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  opponents = player.opponents_for_game( game )
  status = "|"
  if ( opponents and opponents[0] ):
    status += game.state_for_player( opponents[0] )
  else:
    status += "error"
  return HttpResponse( status )

#-------------------------------------------------------------------
# AJAX response for the opponent state
def data_player_state( request, game_id ):
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  status = "|" + game.state_for_player( player )
  return HttpResponse( status )

#-------------------------------------------------------------------
# AJAX response for setting the hands
def tiles_are_set( request, game_id ):
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  pig = game.player_in_game( player )
  pig.player_is_ready( request.GET['set1'], request.GET['set2'], request.GET['set3'] )
  return HttpResponse( "OK" )
  
#-------------------------------------------------------------------
# AJAX response for previewing the set hands
def preview_hands( request, game_id ):
  new_set1 = PGSet.create_with_tile_chars( request.GET['set1'] ).tile_ordering_for_set_hands()
  new_set2 = PGSet.create_with_tile_chars( request.GET['set2'] ).tile_ordering_for_set_hands()
  new_set3 = PGSet.create_with_tile_chars( request.GET['set3'] ).tile_ordering_for_set_hands()
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  pig = game.player_in_game( player )
  pig.player_is_previewing_hands()
  return HttpResponse( "|" + new_set1 + "|" + new_set2 + "|" + new_set3 + "|" )

#-------------------------------------------------------------------
# AJAX response for previewing the set hands
def unpreview_hands( request, game_id ):
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  pig = game.player_in_game( player )
  pig.player_has_unpreviewed_hands()
  return HttpResponse( "OK" )

#-------------------------------------------------------------------
# AJAX response for previewing the opponents tiles when both players
# have finished setting the tiles.
def get_opponent_tiles( request, game_id, pgtile_size ):
  from models import PGPlayerInGame
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  pig = game.player_in_game( player )
  if ( not pig ):
    return HttpResponseNotAllowed( "You are not a player in this game, no peeking!" )
  if ( pig.state() != PGPlayerInGame.READY ):
    return HttpResponseNotAllowed( "You naughty person you: trying to get the opponents tiles before you've finished setting yours!" )
  opponents = player.opponents_for_game( game )
  if ( not opponents ):
    return HttpResponseNotAllowed( "You are not playing anyone in this game.  How can that be?" )
  opponent = opponents[0]
  if ( not opponent ):
    return HttpResponseNotAllowed( "You are playing a ghost in this game.  How can that be?" )
  pigo = game.player_in_game( opponent )
  if ( not pigo ):
    return HttpResponseNotAllowed( "Your opponent is not a player in this game.  How can that be?" )
  if ( pigo.state() != PGPlayerInGame.READY ):
    return HttpResponseNotAllowed( "You naughty person you: trying to get opponents tiles before they have finished setting them!" )
  
  # Finally!  Both players are ready.  Return the background-sprite image locations
  # exactly as they would appear in the style.
  ret_val = "|"
  sets = pigo.sets()
  for pgset in sets:
    tiles = pgset.tiles
    for tile in tiles:
      ret_val += tile.background_position_css_value( pgtile_size ) + ";"
    ret_val += "|"
  return HttpResponse( ret_val )
