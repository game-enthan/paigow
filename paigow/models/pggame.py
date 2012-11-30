# This file defines the PGGame object that represents a single
# playing of a single game.  It may be ended or in the middle.

# See 'models.py' for documentation on this line
from django.db import models

# ----------------------------------------------------
# This represents one game, which may or may not be complete.
# A game can be paused in the middle and its state will be
# saved in the database.  To do this, we need to reconstruct:
#
#   (1) the players that are playing this game
#   (2) the current score for those players
#   (3) what they're doing (waiting for a deal? playing tiles?)
#   (4) the tiles each player is looking at (if they're playing)
#

class PGGame(models.Model):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'

  # name of the game (there may be different types of games)
  name = models.CharField(max_length=100)
  
  # keep track of when the game was started and when it finished;
  # if the finish date is <TBD> then the game is not over
  start_date = models.DateTimeField('start date')
  finish_date = models.DateTimeField('start date')
  
  # A game can be paused in the middle, and we need to keep enough
  # state that the next time the players log in, they can resume
  # where they left off.  Games consiste of a number of "deals", where
  # a deal is the distribution of tiles to each player after washing.
  #
  # Games can be in any of the following states (the two-letter codes
  # are stored in the database, and the text descriptions are for viewing
  # the state on a website or app).
  ABOUT_TO_DEAL =   'BD'   # between deals in an unfinished game; the
                           # game when created is this because it's about
                           # to deal.
  GAME_OVER =       'GO'   # the game is over
  PLAYING =         'PL'   # the players are playing the deal
  
  GAME_STATE_CHOICES = (
    ( ABOUT_TO_DEAL, 'About to deal' ),
    ( PLAYING,       'Playing the tiles' ),
    ( GAME_OVER,     'Game over, dude' ),
  )
  game_state = models.CharField(max_length=2,
                        choices=GAME_STATE_CHOICES,
                        default=ABOUT_TO_DEAL)

  # If the Game is in the middle of a deal when the players have to pause,
  # then in order to resume we need to save enough information that they
  # can get exactly the same tiles in the same order.  We could create a
  # separate table for that, but if we assume that deals to players are
  # always in the same order, then we can just save the original order of
  # the deck and let it re-deal.
  #
  # The database saves every single deal (deck of tiles after washing) for
  # every single game, so this game may have a number of deals in the database
  # associated with it.  Each deal for a given game has a unique deal_index
  # (a small number starting at 1) so we can find the specific deal that is
  # currently being played.  This is that number.
  deal_number = models.PositiveSmallIntegerField()
  
  # This will make the object return value print out as the name of the game.
  def __unicode__(self):
    return self.name



