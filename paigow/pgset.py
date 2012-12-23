# This file defines the PGSet python class.  This class holds four
# PGTiles and has a bunch of convenience functions.  This is not
# kept in the database because it is transient.

from models.pgtile import PGTile

class PGSet:
  
  # make sure the application name is what we want so any command that
  # applies to the 'paigow' application also applies to us, and any
  # configuration that uses the app-name (like database table generation)
  # uses 'paigow'
  class Meta:
    app_label = 'paigow'
  
  tiles = list()
  
  # initialize with the list of tiles
  def __init__( self, tile_list ):
    self.tiles = tile_list
  
  # return the four-char string for the tiles
  def tile_chars( self ):
    return "" + self.tiles[0].char() + self.tiles[1].char() + self.tiles[2].char() + self.tiles[3].char()
  
  # utility to sort the tiles alphabetically for comparison
  @classmethod
  def sort_tile_chars( self, tile_chars ):
    char_array = []
    for c in tile_chars: 
        char_array.append(c)
    return ''.join(sorted(char_array))
  
  def sorted_tile_chars( self ):
    return self.sort_tile_chars( self.tile_chars() )
  
  # return true if the incoming chars are a possible arrangement
  # of this set
  def can_be_rearranged_to( self, tile_chars ):
    return ( self.sorted_tile_chars() == PGSet.sort_tile_chars( tile_chars ) )

  # convenience for creation
  @classmethod
  def create( cls, tile_list ):
    return cls( tile_list = tile_list )
  
  @classmethod
  def create_with_tile_chars( cls, tile_chars ):
    return PGSet.create( ( 
                    PGTile.with_char(tile_chars[0]),
                    PGTile.with_char(tile_chars[1]),
                    PGTile.with_char(tile_chars[2]),
                    PGTile.with_char(tile_chars[3]) ) )


# ----------------------------------------------------
# Test PGSet class

from django.test import TestCase

class PGSetTest( TestCase ):

  # we need the set of tiles in the test database
  fixtures = [ 'pgtile.json' ]
  
  def test_num_tiles( self ):
    set = PGSet.create( ( PGTile.with_name( "teen", True ),
                          PGTile.with_name( "day", True ),
                          PGTile.with_name( "high ten", True ),
                          PGTile.with_name( "eleven", True ), ) )
    self.assertIsNotNone( set )
  
  def test_sorting( self ):
    set = PGSet.create_with_tile_chars( "AaBb" )
    self.assertTrue( set.can_be_rearranged_to( "abAB" ) )
    self.assertTrue( set.can_be_rearranged_to( "aBbA" ) )
    self.assertTrue( set.can_be_rearranged_to( "abAB" ) )
    self.assertFalse( set.can_be_rearranged_to( "abAc" ) )
