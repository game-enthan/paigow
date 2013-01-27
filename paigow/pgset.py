# This file defines the PGSet python class.  This class holds four
# PGTiles and has a bunch of convenience functions.  This is not
# kept in the database because it is transient.

from models.pgtile import PGTile

# Turn this on for logging
s_pgset_logging = False

# Different ways we can auto-set
s_use_numerical_auto_set = False

class PGSet:
  
  # make sure the application name is what we want so any command that
  # applies to the 'paigow' application also applies to us, and any
  # configuration that uses the app-name (like database table generation)
  # uses 'paigow'
  class Meta:
    app_label = 'paigow'
  
  # initialize with the list of tiles
  def __init__( self, tile_list ):
    self.tiles = tile_list
  
  def __unicode__( self ):
    from paigow.pghand import PGHand
    hand1 = PGHand.create_with_tile_chars( self.tiles[0].char(), self.tiles[1].char() )
    hand2 = PGHand.create_with_tile_chars( self.tiles[2].char(), self.tiles[3].char() )
    return "Set: [" + str( hand1 ) + " ] ... [ " + str( hand2 ) + " ]"
  
  def __str__(self):
    return unicode(self).encode('utf-8')  # return the four-char string for the tiles
  
  def tile_chars( self ):
    return "" + self.tiles[0].char() + self.tiles[1].char() + self.tiles[2].char() + self.tiles[3].char()
  
  def hands( self ):
    from paigow.pghand import PGHand
    hand1 = PGHand.create_with_tile_chars( self.tiles[0].char(), self.tiles[1].char() )
    hand2 = PGHand.create_with_tile_chars( self.tiles[2].char(), self.tiles[3].char() )
    return hand1, hand2
  
  # return the high and low hands.
  def high_and_low_hands( self ):
    from paigow.pghand import PGHand
    hand1, hand2 = self.hands()
    if ( hand2.beats( hand1 ) ):
      return hand2, hand1
    else:
      return hand1, hand2
  
  def high_hand( self ):
    from paigow.pghand import PGHand
    high_hand, low_hand = self.high_and_low_hands()
  
  
  # the user has set the first and second tile to a specific hand, and the third and fourth.
  # Keep the hands intact, but switch the hands and the tiles within them to the correct
  # high/low hand, and within that the the high/low tile.
  def tile_chars_for_set_hands( self ):
    from paigow.pghand import PGHand
    high_hand, low_hand = self.high_and_low_hands()
    tile1, tile2 = high_hand.high_tile.char(), high_hand.low_tile.char()
    tile3, tile4 = low_hand.high_tile.char(), low_hand.low_tile.char()
    return "" + tile1 + tile2 + tile3 + tile4
  
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
    return self_high.is_beaten_by(other_high) and self_low.is_beaten_by(other_low)
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
  
  # more specific comparisons
  def has_higher_high_hand_than( self, other ):
    self_high, self_low = self.high_and_low_hands()
    other_high, other_low = other.high_and_low_hands()
    if self_high > other_high:
      return True
    elif other_high > self_high:
      return False
    else:
      return False
  
  # return the sum and diff of this hand
  def sum_and_diff( self ):
    from paigow.pghand import PGHand
    high_hand, low_hand = self.high_and_low_hands()
    high_ranking = high_hand.ranking()
    low_ranking = low_hand.ranking()
    sum = high_ranking + low_ranking
    diff = high_ranking - low_ranking
    return sum, diff

  # return the sum and diff of this hand
  def hand_ranking_diff( self ):
    sum, diff = self.sum_and_diff()
    return diff
  
  # return the sum and diff of this hand
  def hand_ranking_sum( self ):
    sum, diff = self.sum_and_diff()
    return sum
  
  # more specific comparisons
  def is_more_even_than( self, other ):
    if self.hand_ranking_diff() < other.hand_ranking_diff():
      return True
    elif other.hand_ranking_diff() < self.hand_ranking_diff():
      return False
    else:
      return True
  
  # more specific comparisons
  def has_higher_sum_than( self, other ):
    if self.hand_ranking_sum() > other.hand_ranking_sum():
      return True
    elif other.hand_ranking_sum() > self.hand_ranking_sum():
      return False
    else:
      return True
  
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

  def ordering_with_tiles( self, i0, i1, i2, i3, tst ):
    from paigow.pghand import PGHand
    return tst( PGHand.create( self.tiles[i0], self.tiles[i1] ) ) or \
           tst( PGHand.create( self.tiles[i2], self.tiles[i3] ) )
        
  def has( self, tst ):
    from paigow.pghand import PGHand
    hand1, hand2 = self.hands()
    return tst( hand1 ) or tst( hand2 )
  
  def ordering_with( self, tst ):
    if self.ordering_with_tiles( 0, 1, 2, 3, tst ):
      return 1
    if self.ordering_with_tiles( 0, 2, 1, 3, tst ):
      return 2
    if self.ordering_with_tiles( 0, 3, 1, 2, tst ):
      return 3
    return None
  
  # analysis of what it might be set to: return an ordering that has a pair
  def ordering_with_pair( self ):
    from paigow.pghand import PGHand
    return self.ordering_with( PGHand.is_pair )
  
  def ordering_with_two_pair( self ):
    if self.tiles[0].copies(self.tiles[1]) and self.tiles[2].copies(self.tiles[3]):
      return 1
    if self.tiles[0].copies(self.tiles[2]) and self.tiles[1].copies(self.tiles[3]):
      return 2
    if self.tiles[0].copies(self.tiles[3]) and self.tiles[1].copies(self.tiles[2]):
      return 3
    return None
  
  def ordering_with_wong( self ):
    from paigow.pghand import PGHand
    return self.ordering_with( PGHand.is_wong )
  
  def ordering_with_gong( self ):
    from paigow.pghand import PGHand
    return self.ordering_with( PGHand.is_gong )
  
  def ordering_with_high_nine( self ):
    from paigow.pghand import PGHand
    return self.ordering_with( PGHand.is_high_nine )
  
  def has_pair( self ):
    from paigow.pghand import PGHand
    return self.has( PGHand.is_pair )
    
  def has_wong( self ):
    from paigow.pghand import PGHand
    return self.has( PGHand.is_wong )
    
  def has_gong( self ):
    from paigow.pghand import PGHand
    return self.has( PGHand.is_gong )
    
  def has_high_nine( self ):
    from paigow.pghand import PGHand
    return self.has( PGHand.is_high_nine )
    
  # convenience for creation
  @classmethod
  def create( cls, tile_list ):
    return cls( tile_list = tile_list )
  
  @classmethod
  def create_with_tile_chars( cls, tile_chars ):
    return PGSet.create( [ 
                    PGTile.with_char(tile_chars[0]),
                    PGTile.with_char(tile_chars[1]),
                    PGTile.with_char(tile_chars[2]),
                    PGTile.with_char(tile_chars[3]) ] )

  @classmethod
  def create_with_tile_names( cls, tile_names ):
    return PGSet.create( [
                    PGTile.with_name(tile_names[0]),
                    PGTile.with_name(tile_names[1]),
                    PGTile.with_name(tile_names[2]),
                    PGTile.with_name(tile_names[3]) ] )


# ----------------------------------------------------
# Test PGSet class

from django.test import TestCase

class PGSetTest( TestCase ):

  # we need the set of tiles in the test database
  fixtures = [ 'pgtile.json' ]
  
  def test_num_tiles( self ):
    set = PGSet.create( [ PGTile.with_name( "teen", True ),
                          PGTile.with_name( "day", True ),
                          PGTile.with_name( "high ten", True ),
                          PGTile.with_name( "eleven", True ) ] )
    self.assertIsNotNone( set )
  
  def test_sorting( self ):
    set = PGSet.create_with_tile_chars( "AaBb" )
    self.assertTrue( set.can_be_rearranged_to( "abAB" ) )
    self.assertTrue( set.can_be_rearranged_to( "aBbA" ) )
    self.assertTrue( set.can_be_rearranged_to( "abAB" ) )
    self.assertFalse( set.can_be_rearranged_to( "abAc" ) )
  
  def test_comparison( self ):
    set1 = PGSet.create_with_tile_names( ( "day", "mixed nine", "teen", "mixed seven" ) )
    high_hand1, low_hand1 = set1.high_and_low_hands()
    self.assertFalse( low_hand1.beats( high_hand1 ) )
    set2 = PGSet.create_with_tile_names( ( "low four", "mixed five", "long six", "low ten" ) )
    high_hand2, low_hand2 = set2.high_and_low_hands()
    self.assertFalse( low_hand2.beats( high_hand2 ) )
    self.assertTrue( set1 > set2 )
  
  def test_analysis( self ):
    set = PGSet.create_with_tile_names( ( "day", "mixed nine", "low ten", "mixed seven" ) )
    self.assertFalse( set.ordering_with_two_pair() )
    self.assertFalse( set.ordering_with_pair() )
    self.assertEqual( set.ordering_with_wong(), 1 )
    self.assertFalse( set.ordering_with_gong() )
    self.assertEqual( set.ordering_with_high_nine(), 3 )
    set = PGSet.create_with_tile_names( ( "mixed nine", "mixed nine", "low ten", "low ten" ) )
    self.assertEqual( set.ordering_with_two_pair(), 1 )
    self.assertEqual( set.ordering_with_pair(), 1 )
    self.assertFalse( set.ordering_with_wong() )
    self.assertFalse( set.ordering_with_gong() )
    self.assertFalse( set.ordering_with_high_nine() )
    set = PGSet.create_with_tile_names( ( "mixed nine", "low four", "low ten", "teen" ) )
    self.assertFalse( set.ordering_with_two_pair() )
    self.assertFalse( set.ordering_with_pair() )
    self.assertEqual( set.ordering_with_wong(), 3 )
    self.assertFalse( set.ordering_with_gong() )
    self.assertFalse( set.ordering_with_high_nine() )
