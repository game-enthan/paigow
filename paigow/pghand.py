# This file defines the PGHand python class.  This class holds two
# PGTiles and has a bunch of convenience functions for showing value,
# figuring out the high/low tiles, and comparing against other hands.

from models.pgtile import PGTile

class PGHand:
  
  low_tile = PGTile()
  high_tile = PGTile()
  
  def __init__(self, tile1, tile2 ):
    if ( tile1 > tile2 ):
      self.high_tile = tile1
      self.low_tile = tile2
    else:
      self.high_tile = tile2
      self.low_tile = tile1
  
  # convenience method for creation
  @classmethod
  def create( cls, tile1, tile2 ):
    return cls( tile1 = tile1, tile2 = tile2 )
  
  # so printout shows the hand.
  def __unicode__( self ):
    return str( self.high_tile ) + " / " + str( self.low_tile )

# ----------------------------------------------------
# Test PGHand class

from django.test import TestCase

class PGGameTest( TestCase ):
  
  # we need the set of tiles in the test database
  fixtures = [ 'pgtile.json' ]
  
