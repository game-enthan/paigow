# These are referenced from 'urls.py'

from django.shortcuts import render_to_response
from django.contrib import messages
from django.core.context_processors import csrf
from django.template import RequestContext

from models.pggame import PGGame
from models.pgplayer import PGPlayer

# utility function to set up the request parameters
def setup_request_params( request ):
  # this call makes sure 'messages' appears in whatever page we serve
  params = RequestContext( request )
  
  # this call protects agains cross-site request forgery
  params.update( csrf( request ) )
  return params

# home page: if they're not logged in, allow them to log in or register.
# if they are logged in, show them the home page (TBD).
def home( request ):
  params = setup_request_params( request )
  if (not request.session.get('player_id', False)):
    messages.add_message( request, messages.INFO, "You are not logged in." )
    return render_to_response( 'user_login.html', params )
  else:
    return render_to_response( 'base_site.html', params )


# register as a new user
def register( request ):
    params = setup_request_params( request )
    return render_to_response( 'user_login.html', params )

def login( request ):
  params = setup_request_params( request )
  player = PGPlayer.objects.filter(name = request.POST['username'])
  if ( not player ):
    messages.add_message(request, messages.ERROR, "Your username and password didn't match.")
    return render_to_response( 'user_login.html', params )
  
  if m.password != request.POST['password']:
    messages.add_message(request, messages.ERROR, "Your username and password didn't match.")
    return render_to_response( 'user_login.html', params )

  # remember this player id in the session and send them to the home page.
  request.session['player_id'] = player.id
  return render_to_response( 'base_site.html', params )

# Send a page to create a new game
def create_game( request ):
  params = setup_request_params( request )
  # test if the user is logged in
  if (not request.session.get('player_id', False)):
    return render_to_response( 'user_login.html', { 'next_page' : 'create_game' } )
  else:
    new_game = PGGame.create( 'enter name' )
    new_game.save()
    return render_to_response( 'game_create.html',
      { 'game': new_game,
        'title': 'New Game'
      } )

# Wrapper view for Templates, may be needed for debugging
from django.views.generic import TemplateView

class PaiGowView(TemplateView):
  
  def nothing(self):
    return nil;
