# This file defines the PGHand python class.  This class holds two
# PGTiles and has a bunch of convenience functions for showing value,
# figuring out the high/low tiles, and comparing against other hands.

from models.pgtile import PGTile

class PGHand:
  
  # make sure the application name is what we want so any command that
  # applies to the 'paigow' application also applies to us, and any
  # configuration that uses the app-name (like database table generation)
  # uses 'paigow'
  class Meta:
    app_label = 'paigow'
  
  low_tile = PGTile()
  high_tile = PGTile()
  
  # so printout shows the hand.
  def __unicode__( self ):
    return str( self.high_tile ) + " / " + str( self.low_tile )

  # when given two tiles, make sure we put them in order.  This makes
  # later comparisons easy.
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
  
  # convenience functions for  naming and comparisons.
  def is_pair( self ):
    return high_tile == low_tile
  def is_wong( self ):
    return high_tile.is_teen_or_day() and (low_tile.tile_value == 9)
  def is_gong( self ):
    return high_tile.is_teen_or_day() and (low_tile.tile_value == 8)
  def is_high_nine( self ):
    return high_tile.is_teen_or_day() and (low_tile.tile_value == 7)
  def numerical_value( self ):
    return ( high_tile.tile_value + low_tile.tile_value ) % 10
  
# ----------------------------------------------------
# Test PGHand class

from django.test import TestCase

class PGHandTest( TestCase ):

  # we need the set of tiles in the test database
  fixtures = [ 'pgtile.json' ]
  
  # test that it correct sets high and low tiles
  def test_tile_ranking( self ):
    '''Test that the tile ranking is correctly parsed on creation'''
    gee_joon = PGTile.with_name( "gee joon" )
    low_four = PGTile.with_name( "low four" )
    hand1 = PGHand.create( gee_joon, low_four )
    self.assertEqual( hand1.low_tile, gee_joon )
    self.assertEqual( hand1.high_tile, low_four )
    hand2 = PGHand.create( low_four, gee_joon )
    self.assertEqual( hand2.low_tile, gee_joon )
    self.assertEqual( hand2.high_tile, low_four )


# run the test when invoked as a test (this is boilerplate
# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()

