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
  
  # these are rankings; however, the zeros are all in a bunch to try to
  # avoid those, since they all compare the same and a 1 is much better.
  s_hand_rankings = {
    'hl': 0, # eleven / mixed nine
    'gk': 0, # low four / low six
    'fg': 0, # long six / low four
    'ei': 0, # high ten / low ten
    'df': 0, # harmony four / long six
    'dk': 0, # harmony four / low six
    'ko': 5, # low six / mixed five
    'hi': 6, # eleven / low ten
    'gj': 7, # low four / high seven
    'gn': 7, # low four / mixed seven
    'fo': 8, # long six / mixed five
    'eh': 9, # high ten / eleven
    'dj': 10, # harmony four / high seven
    'dn': 10, # harmony four / mixed seven
    'no': 11, # mixed seven / mixed five
    'jo': 12, # high seven / mixed five
    'gm': 13, # low four / mixed eight
    'fk': 14, # long six / low six
    'dm': 15, # harmony four / mixed eight
    'cd': 16, # high eight / harmony four
    'cg': 16, # high eight / low four
    'be': 17, # day / high ten
    'bi': 17, # day / low ten
    'ae': 18, # teen / high ten
    'ai': 18, # teen / low ten
    'np': 19, # mixed seven / gee joon
    'mo': 20, # mixed eight / mixed five
    'kn': 21, # low six / mixed seven
    'jp': 22, # high seven / gee joon
    'jk': 22, # high seven / low six
    'gl': 23, # low four / mixed nine
    'fj': 24, # long six / high seven
    'fn': 24, # long six / mixed seven
    'dl': 25, # harmony four / mixed nine   # magic number for low hands
    'co': 26, # high eight / mixed five
    'bh': 27, # day / eleven
    'ah': 28, # teen / eleven
    'mp': 29, # mixed eight / gee joon
    'lo': 30, # mixed nine / mixed five
    'km': 31, # low six / mixed eight
    'jn': 32, # high seven / mixed seven
    'gi': 33, # low four / low ten
    'fm': 34, # long six / mixed eight
    'eg': 35, # high ten / low four
    'de': 36, # harmony four / high ten
    'di': 36, # harmony four / low ten
    'cp': 37, # high eight / gee joon
    'cf': 37, # high eight / long six
    'ck': 37, # high eight / low six
    'ab': 38, # teen / day
    'mn': 39, # mixed eight / mixed seven
    'lp': 40, # mixed nine / gee joon
    'kl': 41, # low six / mixed nine
    'jm': 42, # high seven / mixed eight
    'io': 43, # low ten / mixed five
    'gh': 44, # low four / eleven
    'fl': 45, # long six / mixed nine
    'eo': 46, # high ten / mixed five
    'dh': 47, # harmony four / eleven
    'cj': 48, # high eight / high seven
    'cn': 48, # high eight / mixed seven
    'ln': 49, # mixed nine / mixed seven
    'jl': 50, # high seven / mixed nine
    'ip': 51, # low ten / gee joon
    'ik': 51, # low ten / low six
    'ho': 52, # eleven / mixed five
    'fi': 53, # long six / low ten
    'ep': 54, # high ten / gee joon
    'ef': 54, # high ten / long six
    'ek': 54, # high ten / low six
    'cm': 55, # high eight / mixed eight
    'bd': 56, # day / harmony four
    'bg': 56, # day / low four
    'ad': 57, # teen / harmony four
    'ag': 57, # teen / low four
    'lm': 58, # mixed nine / mixed eight
    'ij': 59, # low ten / high seven
    'in': 59, # low ten / mixed seven
    'hp': 60, # eleven / gee joon
    'hk': 60, # eleven / low six
    'gp': 61, # low four / gee joon
    'fh': 62, # long six / eleven
    'ej': 63, # high ten / high seven
    'en': 63, # high ten / mixed seven
    'dp': 64, # harmony four / gee joon
    'cl': 65, # high eight / mixed nine
    'bo': 66, # day / mixed five
    'ao': 67, # teen / mixed five
    'op': 68, # mixed five / gee joon
    'im': 69, # low ten / mixed eight
    'hj': 70, # eleven / high seven
    'hn': 70, # eleven / mixed seven
    'em': 71, # high ten / mixed eight
    'dg': 72, # harmony four / low four
    'ce': 73, # high eight / high ten
    'ci': 73, # high eight / low ten
    'bp': 74, # day / gee joon
    'bf': 74, # day / long six
    'bk': 74, # day / low six
    'ap': 75, # teen / gee joon
    'af': 75, # teen / long six
    'ak': 75, # teen / low six
    'kp': 76, # low six / gee joon
    'il': 77, # low ten / mixed nine
    'hm': 78, # eleven / mixed eight
    'go': 79, # low four / mixed five
    'fp': 80, # long six / gee joon
    'el': 81, # high ten / mixed nine
    'do': 82, # harmony four / mixed five
    'ch': 83, # high eight / eleven
    'bj': 84, # day / high seven
    'bn': 84, # day / mixed seven
    'aj': 85, # teen / high seven
    'an': 85, # teen / mixed seven
    'bc': 86, # day / high eight
    'bm': 86, # day / mixed eight
    'ac': 87, # teen / high eight
    'am': 87, # teen / mixed eight
    'bl': 88, # day / mixed nine
    'al': 89, # teen / mixed nine
    'oo': 90, # mixed five / mixed five
    'nn': 91, # mixed seven / mixed seven
    'mm': 92, # mixed eight / mixed eight
    'll': 93, # mixed nine / mixed nine
    'kk': 94, # low six / low six
    'jj': 95, # high seven / high seven
    'ii': 96, # low ten / low ten
    'hh': 97, # eleven / eleven
    'gg': 98, # low four / low four
    'ff': 99, # long six / long six
    'ee': 100, # high ten / high ten
    'dd': 101, # harmony four / harmony four
    'cc': 102, # high eight / high eight
    'bb': 103, # day / day
    'aa': 104, # teen / teen
    'pp': 105, # gee joon / gee joon
  }
  
  
  # so printout shows the hand.
  def __unicode__( self ):
    return str( self.high_tile ) + " / " + str( self.low_tile )
  def __str__( self ):
    return unicode(self).encode('utf-8')
 
  # when given two tiles, make sure we put them in order.  This makes
  # later comparisons easy.
  def __init__( self, tile1, tile2 ):
    switch = False
    if tile1.copies(tile2):
      switch = tile1.char() < tile2.char()
    else:
      switch = tile1.is_beaten_by(tile2)
    if switch:
      self.high_tile = tile2
      self.low_tile = tile1
    else:
      self.high_tile = tile1
      self.low_tile = tile2
  
  # convenience method for creation
  @classmethod
  def create( cls, tile1, tile2 ):
    return cls( tile1 = tile1, tile2 = tile2 )
  
  # convenience method for creation
  @classmethod
  def create_with_tile_chars( cls, tile1_char, tile2_char ):
    return PGHand.create( PGTile.with_char( tile1_char ), PGTile.with_char( tile2_char ) )
  @classmethod
  def create_with_tile_names( cls, tile1_name, tile2_name ):
    return PGHand.create( PGTile.with_name( tile1_name ), PGTile.with_name( tile2_name ) )
  
  def tile_chars( self ):
    return str(self.high_tile.char()) + str(self.low_tile.char())
  
  # return the label for this hand
  def label( self ):
    if self.is_gee_joon():
      return "gee joon"
    if self.is_pair():
      return "" + self.high_tile.name + " bo"
    if self.is_wong():
      return "wong" 
    if self.is_gong():
      return "gong" 
    if self.is_high_nine():
      return "high nine"
    return str(self.numerical_value())
  
  def ranking( self ):
    return PGHand.s_hand_rankings[self.tile_chars().lower()]
  
  # convenience functions for  naming and comparisons.
  def is_gee_joon( self ):
    return self.is_pair() and self.high_tile.tile_value == 3
  def is_pair( self ):
    return self.high_tile.copies( self.low_tile )
  def is_wong( self ):
    return self.high_tile.is_teen_or_day() and ( self.low_tile.tile_value == 9 )
  def is_gong( self ):
    return self.high_tile.is_teen_or_day() and ( self.low_tile.tile_value == 8 )
  def is_high_nine( self ):
    return self.high_tile.is_teen_or_day() and ( self.low_tile.tile_value == 7 )
  def numerical_value( self ):
    if ( self.low_tile.is_gee_joon_tile() ):
      num1 = (self.high_tile.tile_value + 3) % 10
      num2 = (self.high_tile.tile_value + 6) % 10
      if ( num1 > num2 ):
        return num1
      else:
        return num2
    else:
      return ( self.high_tile.tile_value + self.low_tile.tile_value ) % 10
  
  # comparison operators
  
  def high_tile_beats( self, other ):
    return self.high_tile.beats( other.high_tile )
  
  def beats( self, other ):
    
    # check gee joon...
    if self.is_gee_joon():
      return True
    elif other.is_gee_joon():
      return False
    # neither is gee_joon...

    # check pairs...
    if other.is_pair():
      if not self.is_pair():
        return False                                # other is a pair, we are not
      return self.high_tile_beats( other )          # both pair, check high tile
    elif self.is_pair():
      return True                                   # we are pair, other is not
    # neither is pair...
    
    # check wongs
    if other.is_wong():
      if not self.is_wong():
        return False                                # other is wong, we are not
      return self.high_tile_beats( other )          # both wong, check high tile
    elif self.is_wong():
      return True                                   # we are wong, other is not
    # neither is wong...
    
    # check gongs
    if other.is_gong():
      if not self.is_gong():
        return False                                # other is gong, we are not
      return self.high_tile_beats( other )          # both gong, check high tile
    elif self.is_gong():
      return True                                   # we are gong, other is not
    # neither is gong...
    
    # check high nine
    if other.is_high_nine():
      if not self.is_high_nine():
        return False                                # other is high nine, we are not
      return self.high_tile_beats( other )          # both high nine, check high tile
    elif self.is_high_nine():
      return True                                   # we are high nine, other is not
    # neither is high nine
    
    # check value
    if self.numerical_value() == other.numerical_value():
      if self.numerical_value() == 0:
        return False                                # special rules: all zeroes are copies
      else:
        return self.high_tile_beats( other )        # same (non-zero) value, return tile comparison
    else:
      return self.numerical_value() > other.numerical_value()  # different values, compare values
  
  def is_beaten_by( self, other ):
    return other.beats( self )
  
  def copies( self, other ):
    return ( not self.beats( other ) ) and ( not other.beats( self ) )
  

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
  
  def test_name( self ):
    teen1 = PGTile.with_name( "teen", True )
    teen2 = PGTile.with_name( "teen", False )
    hand1 = PGHand.create( teen1, teen2 )
    self.assertEqual( hand1.label(), "teen bo" )

  def test_comparison( self ):
    gee_joon = PGTile.with_name( "gee joon" )
    low_four = PGTile.with_name( "low four" )
    teen = PGTile.with_name( "teen" )
    mixed_five = PGTile.with_name( "mixed five" )
    day = PGTile.with_name( "day" )
    hand1 = PGHand.create( gee_joon, low_four )
    hand2 = PGHand.create( teen, mixed_five )
    hand3 = PGHand.create( day, mixed_five )
    hand4 = PGHand.create( teen, day )
    self.assertTrue( hand2.beats(hand1) )
    self.assertFalse( hand2.copies(hand1) )
    self.assertFalse( hand2.is_beaten_by(hand1) )
    self.assertTrue( hand2.beats(hand3) )
    self.assertTrue( hand2.beats(hand4) )
    mixed_seven = PGTile.with_name( "mixed seven" )
    hand1 = PGHand.create( teen, mixed_five )
    hand2 = PGHand.create( teen, mixed_seven )
    self.assertTrue( hand2.beats(hand1) )
    self.assertTrue( hand1.is_beaten_by(hand2) )
  
  def test_comparison2( self ):
    hand11 = PGHand.create( PGTile.with_name( "day", True ),
                            PGTile.with_name( "mixed nine", True ) )
    hand12 = PGHand.create( PGTile.with_name( "teen", True ),
                            PGTile.with_name( "mixed seven", True ) )
    hand21 = PGHand.create( PGTile.with_name( "low four", True ),
                            PGTile.with_name( "mixed five", True ) )
    hand22 = PGHand.create( PGTile.with_name( "long six", True ),
                            PGTile.with_name( "low ten", True ) ) 
    self.assertTrue( hand11.beats( hand21 ) )
    self.assertTrue( hand21.is_beaten_by( hand11 ) )
    self.assertTrue( hand12.beats( hand22 ) )
    self.assertTrue( hand22.is_beaten_by( hand12 ) )
  
  def sort_for_test( self, hand1_chars, hand2_chars ):
    hand1 = PGHand.create_with_tile_chars( hand1_chars[0], hand1_chars[1]  )
    hand2 = PGHand.create_with_tile_chars( hand2_chars[0], hand2_chars[1]  )
    if hand1.beats( hand2 ):
      return 1
    elif hand2.beats( hand1 ):
      return -1
    else:
      return 0
  
  def test_ranking( self ):
    hand1 = PGHand.create_with_tile_names( "gee joon", "low four" )
    self.assertEqual( hand1.ranking(), 61 )

  def test_numerical_value( self ):
    hand1 = PGHand.create_with_tile_names( "long six", "low four" )
    self.assertEqual( hand1.numerical_value(), 0 )
    self.assertEqual( hand1.label(), "0" )


  # def test_create_all_rankings( self ):
  #   print "\n"
  #   all_hands = []
  #   rankings = []
  #   tiles = PGTile.objects.all()
  #   for tile1 in tiles:
  #     for tile2 in tiles:
  #       if tile2 == tile1:
  #         continue
  #       hand = PGHand.create( tile1, tile2 )
  #       hand_chars = hand.tile_chars().lower()
  #       if not hand_chars in all_hands:
  #         all_hands.append( hand_chars )
  #   all_hands.sort(self.sort_for_test)
  #   ranking = 0
  #   last_hand = None
  #   for hand_chars in all_hands:
  #     hand = PGHand.create_with_tile_chars( hand_chars[0], hand_chars[1] )
  #     if last_hand:
  #       if hand.beats(last_hand):
  #         ranking += 1
  #     rankings.append(ranking)
  #     last_hand = hand
  #   for hand, ranking in zip( all_hands, rankings ):
  #     print "" + str(ranking) + ": \"" + str(hand) + "\": " + str(PGHand.create_with_tile_chars(hand[0], hand[1]))
    
    
# run the test when invoked as a test (this is boilerplate
# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()

