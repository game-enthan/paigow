# This file defines the Deal python class, derived from the
# django 'models.Model' class that relates python classes to
# relational database tables.
#
# A 'deal' is the ordering of a deck that implies the tiles
# dealt to each player in a game.  Since the algorithm that
# deals is the same every time, all we need to do is specify
# the ordering of the tiles and that dictates what the players
# will get.
#
# Since there are only sixteen distinct tile in terms of game
# play (regardless of what they look like), we can represent
# each tile as a hex digit and have 32 hex digits that represent
# the ordering of the tiles.
#
# We can distinguish the tiles whose individuals are different
# (like the mixed pairs or gee joon tiles) by assuming the first
# tile is one of them and the second is another, in the order
# they appear in the deck.

from django.db import models

from paigow.models import PGGame
from pgtile import PGTile

class PGDeal( models.Model ):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'
  
  # This 32-character hex string defines the deal
  deck = models.CharField( max_length = 32 )
  
  # it's always part of some game, and some deal number
  game = models.ForeignKey( PGGame )
  deal_number = models.PositiveSmallIntegerField()
  
  # The deal shows as the ordering
  def __unicode__( self ):
    return self.tiles
  
  
  # Create it with an array of tiles and the game/deal#
  @classmethod
  def create( cls, tiles, game, deal_number ):
    from pgtile import PGTile
    deck_vals = ""
    for tile in tiles:
      char = "0123456789ABCDEF"[tile.tile_rank]
      deck_vals += char
    return cls( deck = deck_vals, game = game, deal_number = deal_number )
  
  
  # return the tile for any given offset
  def tile( self, offset ):
    
    # sanity check
    if ( offset < 0 or offset > 31 ):
      return None
    
    # get the char and we'll index it into tiles... but
    # we want to decide if it's the first or second
    tile_rank_char = self.deck[offset]
    
    # loop to check if it's the first or not    
    offset_check = 0
    is_first = (self.deck.index( tile_rank_char ) == offset)
    
    # return the appropriate number
    return PGTile.with_rank( int(str(tile_rank_char), 16), is_first )


# ----------------------------------------------------
# Test PGDeal class

from django.test import TestCase

class PGDealTest( TestCase ):
  
  fixtures = [ 'pgtile.json' ]
  
  def test_basic( self ):
    from pggame import PGGame
    
    tiles = PGTile.objects.all()
    game = PGGame.create( "Test for PGDeal" )
    deal = PGDeal.create( tiles, game, 0 )
    self.assertIsNone( deal.tile( -1 ) )
    for i in range(32):
      self.assertIsNotNone( deal.tile( i ) )
    self.assertIsNone( deal.tile( 32 ) )

# run the test when invoked as a test (this is boilerplate
# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()


