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
from models.pgplayerindeal import PGPlayerInDeal
from paigow.pgset import PGSet

from paigow.session_utils import session_player, session_opponent, opponent_in_session_deal, player_in_session_deal

# put this at the beginning of any function to start debugging it, if we have a local django server
#  import pdb; pdb.set_trace()


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
  from django.utils.html import escape
  
  # protect against cross-site request forgery
  params.update( csrf( request ) )
  
  # set up the URLs for the app-wide menus
  params['logout_url'] = '/paigow/logout'
  params['home_url'] = '/paigow/home'
  
  params['activities'] = (
      { 'name': "Start New Game", 'url': '/paigow/game/new' }, )
  
  # setup players and possible opponents
  player = session_player( request )
  params['player'] = player
  if ( not player ):
    request.session['player_id'] = None
    params['playername'] = None
    params['opponents'] = None
    params['opponent'] = None
  else:
    params['playername'] = escape(player.name)
    params['opponents'] = player.all_possible_opponents()
    if ( 'game' in params ):
      game = params['game']
      params['opponent'] = player.opponent_for_deal( game, params['deal_number'] )
      params['title'] = "Pai Gow 321: " + escape( game.name )
      params['game_state'] = game.state()
  
  
  # set up the states
  params['tiles_are_set_state'] = PGPlayerInDeal.state_ui( PGPlayerInDeal.READY )
  params['setting_tiles_state'] = PGPlayerInDeal.state_ui( PGPlayerInDeal.SETTING_TILES )
  params['preview_hands_state'] = PGPlayerInDeal.state_ui( PGPlayerInDeal.PREVIEW_HANDS )

  return RequestContext( request, params )


#-------------------------------------------------------------------
# make sure we are redirected to the right place
def goto_home( request, params = {} ):
  return redirect( '/paigow/home', request, params )


#-------------------------------------------------------------------
# home page: if they're not logged in, allow them to log in or register.
# if they are logged in, show them the home page (TBD).
def home( request, params = {} ):
  
  player = session_player( request )
  if not player:
    return render_to_response( 'user_login.html', request_context( request, params ) )
  
  params['games'] = session_player( request ).games()
  params['all_opponents_in_all_games'] = session_player( request ).all_opponents_in_all_games()
  wins, losses = session_player( request ).overall_record()
  params['overall_record'] = str(wins) + " - " + str(losses)
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
  
  # if they don't hit 'remember me' then don't save the cookie
  if not request.POST.get('register_remember_me', None):
    request.session.set_expiry(0)
  
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
  
  # if they don't hit 'remember me' then don't save the cookie
  if not request.POST.get('login_remember_me', None):
    request.session.set_expiry(0)
  
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
  #   player = session_player( request )
  #   if not player:
  #     return goto_home( request )
  return render_to_response( 'game_create.html', request_context( request, params ) )


#-------------------------------------------------------------------
# User clicked 'New Game': return a form so they can create one.
def new_game_against( request, opponent_id, params = {} ):
  player = session_player( request )
  if not player:
    print "Error: new game but no player"
    return goto_home( request )
  opponents = PGPlayer.objects.filter( id = opponent_id )
  if not opponents:
    print "Error: new game but no opponents found id " + str(opponent_id)
    return goto_home( request )
  if len(opponents) != 1:
    print "Error: multiple opponents found for id " + str(opponent_id)
    return goto_home( request )
  params['opponent'] = opponents[0]
  return new_game( request, params )


#-------------------------------------------------------------------
# User clicked 'Add Game' after filling in a game: add it and save it,
# and go home.
def add_game( request, params = {} ):
  
  player = session_player( request )
  if not player:
    return goto_home( request )
  
  # create a new game
  game = PGGame.create( request.POST['game_name'] )
  game.save() # must be done before adding player, so we have an ID
  
  # add ourselves and the opponent (which automatically saves)
  game.add_player( session_player( request ) )
  game.add_player( posted_player_from_id_field( request, 'game_opponent' ) )
  
  messages.add_message( request, messages.INFO, "Game \"" + game.name + "\" created." )
  
  return redirect ( "/paigow/game/" + str(game.id) + "/1" )


#-------------------------------------------------------------------
# User clicked a URL that corresponds to a game.
def play_game( request, game_id, deal_number_str, params = {} ):
  
  from models.pgtile import PGTile
  from pghand import PGHand
  
  player_id = request.session.get('player_id', False) 
  if ( not player_id ):
    return goto_home( request )
  player = PGPlayer.objects.get( id = player_id )
  
  # get the game from the db
  game = PGGame.with_id( game_id )
  if ( not game ):
    messages.add_message( request, messages.ERROR, "WTF?  That game has disappeared into the ether (which doesn't exist)" )
    return goto_home( request )
  params['game'] = game

  # get the deal number
  deal_number = int( deal_number_str )
  params['deal_number'] = deal_number
  
  # set the score for the other player.
  players_in_game = game.players()
  
  # make sure you're in the game: you can't look at other games.
  if not ( player in players_in_game ):
    messages.add_message( request, messages.ERROR, "I'm sorry, you are not allowed in that game, it's only for VIPs" )
    return goto_home( request )
  
  # this sets up pig, don't get it fgirst
  params['pgsets'] = game.sets_for_player( session_player( request ), deal_number )

  # set the game and score for you
  pid = game.player_in_deal( player, deal_number )
  params['score_player'] = game.score_as_of_deal_for_player( player, deal_number )
  
  # set up the opponent for the template
  opponent = session_player( request ).opponent_for_deal( game, deal_number )
  
  # get your opponent's score
  #pido = game.player_in_deal( opponent, deal_number )
  params['score_opponent'] = game.score_as_of_deal_for_player( opponent, deal_number )
  
  # create the hands for this player (sets_for_player should be called first)
  params['pgtile_size'] = "medium"
  params['current_player_state'] = PGPlayerInDeal.state_ui( pid.state() )
  
  return render_to_response( 'game_play.html', request_context( request, params ) )

#-------------------------------------------------------------------
# User clicked on "Next Deal" in a game.
def next_deal( request, game_id, deal_number_str, params = {} ):
  game = PGGame.objects.get( id = game_id )
  deal_number = int( deal_number_str )
  
  # find out what the state of this deal is.  If the game is over,
  # show a message a we'll re-show the current tiles.
  game_deal_state = game.deal_state( deal_number )
  if ( game_deal_state == PGGame.GAME_OVER ):
    messages.add_message( request, messages.ERROR, "Game \"" + game.name + "\" is history... get over it, dude." )
  
  # if the deal hasn't finished, then we'll show the error and re-show the tiles
  elif ( game_deal_state == PGGame.SETTING_TILES ):
    messages.add_message( request, messages.ERROR, "You're not done with this deal, you can't get the next!" )
  else:
    
    # valid that someone is asking for a deal; if they've caught up, we'll
    # deal the tiles; otherwise we'll just show whatever deal they have.
    deal_number += 1
    if ( game.current_deal_number < deal_number ):
      game.game_state = PGGame.ABOUT_TO_DEAL
      game.deal_tiles()
    game.assure_players_for_deal( deal_number )
  return redirect( '/paigow/game/' + str( game_id ) + '/' + str( deal_number )  )

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
def data_opponent_state( request, game_id, deal_number ):
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  opponent = player.opponent_for_deal( game, deal_number )
  status = "|"
  if ( opponent ):
    status += game.state_for_player( opponent, deal_number )
  else:
    status += "error"
  return HttpResponse( status )

#-------------------------------------------------------------------
# AJAX response for the opponent state
def data_player_state( request, game_id, deal_number ):
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  status = "|" + game.state_for_player( player, deal_number )
  return HttpResponse( status )

#-------------------------------------------------------------------
# AJAX response for setting the hands
def tiles_are_set( request, game_id, deal_number ):
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  pgpid = game.player_in_deal( player, deal_number )
  pgpid.player_is_ready( request.GET['set1'], request.GET['set2'], request.GET['set3'] )
  return HttpResponse( "OK" )
  
#-------------------------------------------------------------------
# AJAX response for previewing the set hands
def preview_hands( request, game_id, deal_number ):
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
def unpreview_hands( request, game_id, deal_number ):
  game = PGGame.objects.get( id = game_id )
  player = session_player( request )
  pig = game.player_in_game( player )
  pig.player_has_unpreviewed_hands()
  return HttpResponse( "OK" )

#-------------------------------------------------------------------
# AJAX response for previewing the opponents tiles when both players
# have finished setting the tiles.
def get_opponent_tile_background_position_css_value( request, game_id, deal_number, pgtile_size ):
  pigo = opponent_in_session_deal( request, game_id, deal_number )
  if not pigo:
    return HttpResponseNotAllowed( "Bad Request" )
  return HttpResponse( pigo.background_position_css_value( pgtile_size ) )

#-------------------------------------------------------------------
# AJAX response for previewing the opponents tiles when both players
# have finished setting the tiles.
def data_opponent_hand_label( request, game_id, deal_number, set_num ):
  pigo = opponent_in_session_deal( request, game_id, deal_number )
  if not pigo:
    return HttpResponseNotAllowed( "Bad Request" )
  return HttpResponse( pigo.set(int(set_num)).hand_labels() )

#-------------------------------------------------------------------
# AJAX response for result of the three hands
def score_in_deal( request, game_id, deal_number ):
  
  # get the player-in-game so we can get their hands.  Note that if
  # we try to get an opponent but either the player or the the
  # opponent is not finished, we will get None and return bad request
  pgpido = opponent_in_session_deal( request, game_id, deal_number )
  if not pgpido:
    return HttpResponseNotAllowed( "Bad Request" )
  pgpid = player_in_session_deal( request, game_id, deal_number )
  if not pgpid:
    return HttpResponseNotAllowed( "Bad Request" )
  
  # for each set, return W for win, . for push and L for loss
  ret_val = pgpid.win_lose_string_against( pgpido )
  return HttpResponse(ret_val)

#-------------------------------------------------------------------
# AJAX response for the score of the game
def game_score( request, game_id, deal_number_str ):
  deal_number = int( deal_number_str )
  game = PGGame.with_id( game_id )
  player = session_player( request )
  if not player:
    return HttpResponseNotAllowed( "Bad Request" )
  opponent = session_opponent( request, game, deal_number )
  if not opponent:
    return HttpResponseNotAllowed( "Bad Request" )
  return HttpResponse( str( game.score_as_of_deal_for_player( player, deal_number+1 ) ) + " - " + str( game.score_as_of_deal_for_player( opponent, deal_number+1 ) ) )
