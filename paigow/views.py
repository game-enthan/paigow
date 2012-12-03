# These are referenced from 'urls.py'

from django.shortcuts import render_to_response
from models.pggame import PGGame

# Send a page to create a new game
def create_game( request ):
  new_game = PGGame.create('enter name')
  new_game.save()
  return render_to_response('game_create.html', {'game': new_game})


# Wrapper view for Templates, may be needed for debugging
from django.views.generic import TemplateView

class PaiGowView(TemplateView):
  
  def nothing(self):
    return nil;
