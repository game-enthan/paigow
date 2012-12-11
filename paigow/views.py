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
# protect against cross-site request forgery, and put it into a RequestContext
# so the middleware infrastructure like 'messages' works.
def request_context( request, params ):

  params.update( csrf( request ) )
  player = session_player( request )
  if ( not player ):
    request.session['player_id'] = None
  else:
    params['playername'] = player.name
  return RequestContext( request, params )


#-------------------------------------------------------------------
# home page: if they're not logged in, allow them to log in or register.
# if they are logged in, show them the home page (TBD).
def home( request, params = {} ):
  
  if (not request.session.get('player_id', False)):
    return render_to_response( 'user_login.html', request_context( request, params ) )
  else:
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
  
  return redirect( 'home', params )


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
  
  return redirect( 'home', params )


#-------------------------------------------------------------------
# The user chose 'Logout' from the user menu
def logout( request, params = {} ):
  
  request.session['player_id'] = None
  return redirect( 'home', params )


#-------------------------------------------------------------------
# User clicked 'New Game': return a form so they can create one.
def new_game( request, params = {} ):
  
  if (not request.session.get('player_id', False)):
    return render_to_response( 'user_login.html', request_context( request, params ) )
  else:
    return render_to_response( 'game_create.html', request_context( request, params ) )


#-------------------------------------------------------------------
# User clicked 'Add Game' after filling in a game: add it and save it,
# and go home.
def add_game( request, params = {} ):
  
  if (not request.session.get('player_id', False)):
    return render_to_response( 'user_login.html', request_context( request, params ) )
  else:
    game = PGGame.create( request.POST['game_name'] )
    game.save() # must be done before adding player, so we have an ID
    game.add_player( session_player( request ) )
    
    # redirect back home, but since we're under 'game/add', we have to go up one level,
    # and so far I can't figure out how to make "../home" work without errors.
    return redirect( '/paigow/home', params )


