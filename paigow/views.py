# These are referenced from 'urls.py'

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.core.context_processors import csrf
from django.template import RequestContext

from models.pggame import PGGame
from models.pgplayer import PGPlayer




#-------------------------------------------------------------------
# convenience
# return the PGPlayer with the current request session id
def session_player( request ):
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

  #   
  game = PGGame.create( request.POST['game_name'] )
  game.save() # must be done before adding player, so we have an ID
  
  print "game opponent id: " + request.POST['game_opponent'] + "\n"
  
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
  
  if (not request.session.get('player_id', False)):
    return goto_home( request )
  
  game = PGGame.with_id( game_id )
  if ( not game ):
    messages.add_message( request, messages.ERROR, "Cannot find that game, I'm sure it was around here somewhere!" )
    return goto_home( request )
  
  params['game'] = game
  params['opponent'] = session_player( request ).opponents_for_game( game )[0]
  #params['hand'] = PGHand.create( PGTile.objects.get( id = 13 ), PGTile.objects.get( id = 4 ) )
  params['hand'] = PGHand.create( PGTile.create_by_name( "harmony four" ), PGTile.create_by_name( "gee joon" ) )
  return render_to_response( 'game_play.html', request_context( request, params ) )


