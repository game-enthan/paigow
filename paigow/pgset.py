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
  
  def __unicode__( self ):
    return "Set: " + self.tile_chars()
  
  # return the four-char string for the tiles
  def tile_chars( self ):
    return "" + self.tiles[0].char() + self.tiles[1].char() + self.tiles[2].char() + self.tiles[3].char()
  
  # the user has set the first and second tile to a specific hand, and the third and fourth.
  # Keep the hands intact, but switch the hands and the tiles within them to the correct
  # high/low hand, and within that the the high/low tile.
  def tile_chars_for_set_hands( self ):
    from paigow.pghand import PGHand
    high_hand = PGHand.create_with_tile_chars( self.tiles[0].char(), self.tiles[1].char() )
    low_hand = PGHand.create_with_tile_chars( self.tiles[2].char(), self.tiles[3].char() )
    if ( low_hand > high_hand ):
      high_hand, low_hand = low_hand, high_hand
    tile1, tile2 = high_hand.high_tile.char(), high_hand.low_tile.char()
    tile3, tile4 = low_hand.high_tile.char(), low_hand.low_tile.char()
    return "" + tile1 + tile2 + tile3 + tile4
  
  # return the high and low hands.
  def high_and_low_hands( self ):
    from paigow.pghand import PGHand
    hand1 = PGHand.create_with_tile_chars( self.tiles[0].char(), self.tiles[1].char() )
    hand2 = PGHand.create_with_tile_chars( self.tiles[2].char(), self.tiles[3].char() )
    if ( hand1 >= hand2 ):
      return hand1, hand2
    else:
      return hand2, hand1
  
  # the user has set the first and second tile to a specific hand, and the third and fourth.
  # Keep the hands intact, but switch the hands and the tiles within them to the correct
  # high/low hand, and within that the the high/low tile.  Return the re-ordering from 
  # zero to three.
  def tile_ordering_for_set_hands( self ):
    from paigow.pghand import PGHand
    high_hand, low_hand = self.high_and_low_hands()
    tile0, tile1 = high_hand.high_tile, high_hand.low_tile
    tile2, tile3 = low_hand.high_tile, low_hand.low_tile
    ordering_str = str( self.tiles.index(tile0) ) + str( self.tiles.index(tile1) ) + str( self.tiles.index(tile2) ) + str( self.tiles.index(tile3) )
    return ordering_str
  
  # return the hand label for the hands, separated by "|"
  def hand_labels( self ):
    from paigow.pghand import PGHand
    high_hand = PGHand.create_with_tile_chars( self.tiles[0].char(), self.tiles[1].char() )
    low_hand = PGHand.create_with_tile_chars( self.tiles[2].char(), self.tiles[3].char() )
    return high_hand.label() + "|" + low_hand.label()
  
  # return win/tie/lose against a second set.  Makes sure the hands are in high/low order,
  # and within the hands the tiles are in high/low order (but does not make different
  # hands that are already there).  These are numerical comparisons:
  # > means win
  # == means push
  # < means lose
  # note that we are defining some in terms of others: each depends on one or more above it
  def __lt__( self, other ):
    self_high, self_low = self.high_and_low_hands()
    other_high, other_low = other.high_and_low_hands()
    return self_high < other_high and self_low < other_low
  def __eq__( self, other ):
    return not (self < other or other < self)
  def __ne__( self, other ):
    return not (self == other)
  def __le__( self, other ):
    return self < other or self == other
  def __ge__( self, other ):
    return other < self or other == self
  def __gt__( self, other ):
    return other < self
  
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
