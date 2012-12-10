# These are referenced from 'urls.py'

from django.shortcuts import render_to_response
from django.contrib import messages
from django.core.context_processors import csrf
from django.template import RequestContext

from models.pggame import PGGame
from models.pgplayer import PGPlayer

# protect against cross-site request forgery, and put it into a RequestContext
# so the middleware infrastructure like 'messages' works.
def request_context( request, params ):
  params.update( csrf( request ) )
  if ( request.session['player_id'] ):
    player = PGPlayer.objects.filter( id = request.session['player_id'] )
    if ( not player ):
      request.session['player_id'] = None
    else:
      params['playername'] = player[0].name
  return RequestContext( request, params )

# home page: if they're not logged in, allow them to log in or register.
# if they are logged in, show them the home page (TBD).
def home( request, params = {} ):
  if (not request.session.get('player_id', False)):
    messages.add_message( request, messages.INFO, "You are not logged in." )
    return render_to_response( 'user_login.html', request_context( request, params ) )
  else:
    return render_to_response( 'home.html', request_context( request, params ) )



# the user clicked the 'Register' button on the login page
def register( request ):
  params = {}
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
  request.session['player_id'] = player.id
  return render_to_response( 'user_login.html', request_context( request, params ) )

# the user clicked the 'Register' button on the login page
def login( request ):
  params = {}
  username = request.POST['login_username']
  if ( not username ):
    params['username'] = username
    messages.add_message(request, messages.ERROR, "Please provide a username.")
    return render_to_response( 'user_login.html', request_context( request, params ) )
  
  player = PGPlayer.objects.filter( name = username )
  if ( not player ):
    messages.add_message(request, messages.ERROR, "Your username and/or password didn't match.")
    params['username'] = username
    return render_to_response( 'user_login.html', request_context( request, params ) )
  
  password = request.POST['login_password']
  if password != request.POST['login_password']:
    messages.add_message(request, messages.ERROR, "Your username and/or password didn't match.")
    return render_to_response( 'user_login.html', request_context( request, params ) )

  # remember this player id in the session and send them to the home page.
  request.session['player_id'] = player[0].id
  return home( request, params )


# log out
def logout( request ):
  request.session['player_id'] = None
  return home( request )


# Send a page to create a new game
def create_game( request ):
  params = {}
  # test if the user is logged in
  if (not request.session.get('player_id', False)):
    return render_to_response( 'user_login.html', request_context( request, params ) )
  else:
    new_game = PGGame.create( 'enter name' )
    new_game.save()
    params.extend( { 'game': new_game, 'title': 'New Game' } )
    return render_to_response( 'game_create.html', request_context( request, params ) )



# Wrapper view for Templates, may be needed for debugging
from django.views.generic import TemplateView

class PaiGowView(TemplateView):
  
  def nothing(self):
    return nil;
