# This file defines the PGGame object that represents a single
# playing of a single game.  It may be ended or in the middle.

# See 'models.py' for documentation on this line
from django.db import models

from django.utils import timezone 

# ----------------------------------------------------
# This represents one game, which may or may not be complete.
# A game can be paused in the middle and its state will be
# saved in the database.  To do this, we need to reconstruct:
#
#   ( 1 ) the players that are playing this game
#   ( 2 ) the current score for those players
#   ( 3 ) what they're doing ( waiting for a deal? playing tiles? )
#   ( 4 ) the tiles each player is looking at ( if they're playing )
#

class PGGame( models.Model ):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'
  
  # allow creation with default fields
  @classmethod
  def create( cls, name ):
    return cls( 
      name = name,
      start_date = timezone.now(),
      game_state = PGGame.ABOUT_TO_DEAL,
      current_deal_number = 0 )

  # name of the game ( there may be different types of games )
  name = models.CharField( max_length=100 )
  
  # keep track of when the game was started and when it finished;
  # if the finish date is <TBD> then the game is not over
  start_date = models.DateTimeField( 'start date' )
  finish_date = models.DateTimeField( 'finish date', null = True )
  
  # A game can be paused in the middle, and we need to keep enough
  # state that the next time the players log in, they can resume
  # where they left off.  Games consiste of a number of "deals", where
  # a deal is the distribution of tiles to each player after washing.
  #
  # Games can be in any of the following states ( the two-letter codes
  # are stored in the database, and the text descriptions are for viewing
  # the state on a website or app ).
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
  game_state = models.CharField(
    max_length = 2,
    choices = GAME_STATE_CHOICES,
    default = ABOUT_TO_DEAL )

  # If the Game is in the middle of a deal when the players have to pause,
  # then in order to resume we need to save enough information that they
  # can get exactly the same tiles in the same order.  We could create a
  # separate table for that, but if we assume that deals to players are
  # always in the same order, then we can just save the original order of
  # the deck and let it re-deal.
  #
  # The database saves every single deal ( deck of tiles after washing ) for
  # every single game, so this game may have a number of deals in the database
  # associated with it.  Each deal for a given game has a unique deal_index
  # ( a small number starting at 1 ) so we can find the specific deal that is
  # currently being played.  This is that number.
  current_deal_number = models.PositiveSmallIntegerField()
  
  # convenience
  @classmethod
  def with_id( cls, game_id ):
    if ( game_id ):
      games = PGGame.objects.filter( id = game_id )
      if ( games.count() > 0 ):
        return games[0]
    return None
  
  # This will make the object return value print out as the name of the game.
  def __unicode__( self ):
    return self.name
  
  # Return the all the players for this single game.
  def players( self ):
    players = []
    from models import PGPlayerInGame
    pigs = PGPlayerInGame.objects.filter( game = self )
    for pig in pigs:
      players.append( pig.player )
    return players

  # Add a player to this game
  def add_player( self, player ):
    from pgplayer import PGPlayer
    from models import PGPlayerInGame
    player = PGPlayerInGame.create( self, player )
    player.save()
  
  # Get the deal given the deal number
  def deal( self, deal_number ):
    from pgdeal import PGDeal
    deals = PGDeal.objects.filter( game = self, deal_number = deal_number )
    
  # Get the current deal
  def current_deal( self ):
    return self.deal( current_deal_number )
    
  
  # shuffle the deck and save it as the current deal
  def create_deal( self ):

    from pgtile import PGTile
    from pgdeal import PGDeal

    # We had better be about to deal
    if ( self.game_state != PGGame.ABOUT_TO_DEAL ):
      raise Exception( 'Trying to deal in wrong state!' )

    # get a shuffled set of tiles
    tiles = PGTile.get_shuffled_tiles()

    # it's a new deal number
    self.current_deal_number += 1

    # remember this deal
    deal = PGDeal.create( tiles, self, self.current_deal_number )
    deal.save()

# ----------------------------------------------------
# Test PGGame class

from django.test import TestCase

class PGGameTest( TestCase ):

  fixtures = [ 'pgtile.json' ]

  def setUp( self ):
    # TBD: don't use database, since that makes this an integratino test
    # rather than a unit test.  That may take re-architecting things.
    self.test_game = PGGame.create( 'paigow321' )
    self.test_game.save()

#   def tearDown( self ):
#     <do something here if necessary>

  def test_add_player( self ):
    '''Adding two players results in a game with 2 players'''
    from pgplayer import PGPlayer
    player_1 = PGPlayer.objects.create( name = 'Rudi' )
    player_2 = PGPlayer.objects.create( name = 'Dave' )
    self.test_game.add_player( player_1 )
    self.test_game.add_player( player_2 )
    self.assertEqual( len(self.test_game.players()), 2 )
    self.assertIn( player_1, self.test_game.players() )
    self.assertIn( player_2, self.test_game.players() )

  def test_deal_x( self ):
    from pgdeal import PGDeal
    self.assertEqual( self.test_game.current_deal_number, 0 )
    self.test_game.create_deal();
    self.assertEqual( self.test_game.current_deal_number, 1 )
    tiles_in_deal = PGDeal.objects.filter( game = self.test_game, deal_number = 1 )
    self.assertEqual( tiles_in_deal.count(), 1 )
  


# run the test when invoked as a test (this is boilerplate
# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()


