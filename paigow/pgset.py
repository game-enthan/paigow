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
  
  # return the high and low hands.
  def high_and_low_hands( self ):
    from paigow.pghand import PGHand
    hand1 = PGHand.create_with_tile_chars( self.tiles[0].char(), self.tiles[1].char() )
    hand2 = PGHand.create_with_tile_chars( self.tiles[2].char(), self.tiles[3].char() )
    if ( hand2.beats( hand1 ) ):
      return hand2, hand1
    else:
      return hand1, hand2
  
  def ranking_stats_for_hands( self, hand1, hand2 ):
    ranking1 = hand1.ranking()
    ranking2 = hand2.ranking()
    if ranking2 > ranking1:
      hand1, hand2 = hand2, hand1
      ranking1, ranking2 = ranking2, ranking1
    return ranking1 + ranking2, ranking1 - ranking2
  
  def switch_tiles( self, index1, index2 ):
    temp = self.tiles[index1]
    self.tiles[index1] = self.tiles[index2]
    self.tiles[index2] = temp
  
  def choose_ordering( self, sum1, diff1, sum2, diff2 ):
    if diff1 < diff2:
      return 1
    elif diff2 < diff1:
      return -1
    elif sum1 > sum2:
      return 1
    elif sum2 > sum1:
      return -1
    else:
      return 0
  
  def sum_and_diff( self ):
    from paigow.pghand import PGHand
    hand1 = PGHand.create( self.tiles[0], self.tiles[1] )
    hand2 = PGHand.create( self.tiles[2], self.tiles[3] )
    if hand2.beats( hand1 ):
      hand1, hand2 = hand2, hand1
    sum, diff = self.ranking_stats_for_hands( hand1, hand2 )
    # print "\n[ " + str(hand1) + " ] + [ " + str(hand2) + " ]:"
    # print"     hand1: " + str(hand1.ranking()) + "  hand2: " + str(hand2.ranking())
    # print"     sum: " + str(sum) + "  diff: " + str(diff)
    return sum, diff
  
  # we have two sets that are not only way. choose between them.
  def first_set_is_better( self, set1, set2 ):
    from paigow.pghand import PGHand
    sum1, diff1 = set1.sum_and_diff()
    sum2, diff2 = set2.sum_and_diff()
    if diff1 < diff2:
      return True
    elif diff2 < diff2:
      return False
    else:
      return True
  
  def reorder_tiles_for_setting( self ):
    if self.tiles[1].beats( self.tiles[0] ):
      self.switch_tiles( 0, 1 )
    if self.tiles[3].beats( self.tiles[2] ):
      self.switch_tiles( 2, 3 )
  
  def reorder_hands_for_setting( self, ordering ):
    if ordering == 2:
      self.switch_tiles( 1, 2 )
    elif ordering == 3:
      self.switch_tiles( 1, 3 )
    self.reorder_tiles_for_setting()
  
  def auto_set_hands( self ):
    from paigow.pghand import PGHand
    
    picked_ordering = -1
    
    # create sets with the three possible combinations
    tiles1 = [ self.tiles[0], self.tiles[1], self.tiles[2], self.tiles[3] ]
    tiles2 = [ self.tiles[0], self.tiles[2], self.tiles[1], self.tiles[3] ]
    tiles3 = [ self.tiles[0], self.tiles[3], self.tiles[1], self.tiles[2] ]
    set1 = PGSet.create( tiles1 )
    set2 = PGSet.create( tiles2 )
    set3 = PGSet.create( tiles3 )
    
    # convenience vars to test various combinations
    s1beats2 = set1 > set2
    s2beats1 = set2 > set1
    s1beats3 = set1 > set3
    s3beats1 = set3 > set1
    s2beats3 = set2 > set3
    s3beats2 = set3 > set2
    
    # see if there is an only-way in there
    if s1beats2 and s1beats3:
      picked_ordering = 1
    elif s2beats1 and s2beats3:
      picked_ordering = 2
    elif s3beats1 and s3beats2:
      picked_ordering = 3
    else:
      
      # nope, no only way.  See if there is any set we can remove
      # so we can just compare the other two
      ignore1 = s2beats1 or s3beats1
      ignore2 = s1beats2 or s3beats2
      ignore3 = s2beats3 or s1beats3
      
      if ignore1:
        if self.first_set_is_better( set2, set3 ):
          picked_ordering = 2
        else:
          picked_ordering = 3
      elif ignore2:
        if self.first_set_is_better( set1, set3 ):
          picked_ordering = 1
        else:
          picked_ordering = 3
      elif ignore3:
        if self.first_set_is_better( set1, set2 ):
          picked_ordering = 1
        else:
          picked_ordering = 2
      else:
        # bleah, need 3-way comparison, no only ways between.
        # choose the one with the smallest difference.
        sum1, diff1 = set1.sum_and_diff()
        sum2, diff2 = set2.sum_and_diff()
        sum3, diff3 = set3.sum_and_diff()
        if diff1 < diff2 and diff1 < diff3:
          picked_ordering = 1
        elif diff2 < diff1 and diff2 < diff3:
          picked_ordering = 2
        elif diff3 < diff1 and diff3 < diff2:
          picked_ordering = 3
        else:
          # double-bleah: there was evidently a diff tie.
          # We can't then go to the largest sum because two with a diff
          # tie, where one sum is larger, would be an only way.  So therefore
          # the two with the smallest diff must be the same.  Therefore,
          # since there are two of them, either 1 or 2 has to be it: just
          # compare those.
          if self.first_set_is_better( set1, set2 ):
            picked_ordering = 1
          else:
            picked_ordering = 2
    
    # we founds something, re-order the tiles for it.
    if picked_ordering > 0:
      self.reorder_hands_for_setting( picked_ordering )
    else:
      print "WTF? auto_sort didn't find anything?"
    return picked_ordering
  
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
  
  def test_auto_sort( self ):
    set1 = PGSet.create_with_tile_names( ( "teen", "low six", "harmony four", "long six" ) )
    self.assertEqual( set1.auto_set_hands(), 2 )
    set1 = PGSet.create_with_tile_names( ( "low four", "mixed nine", "high eight", "mixed eight" ) )
    self.assertEqual( set1.auto_set_hands(), 1 )
    set1 = PGSet.create_with_tile_names( ( "teen", "low ten", "eleven", "mixed nine" ) )
    self.assertEqual( set1.auto_set_hands(), 2 )

