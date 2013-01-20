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
  def __str__( self ):
    return unicode(self).encode('utf-8')
 
  # when given two tiles, make sure we put them in order.  This makes
  # later comparisons easy.
  def __init__(self, tile1, tile2 ):
    if ( not tile1.is_beaten_by(tile2) ):
      self.high_tile = tile1
      self.low_tile = tile2
    else:
      self.high_tile = tile2
      self.low_tile = tile1
  
  # convenience method for creation
  @classmethod
  def create( cls, tile1, tile2 ):
    return cls( tile1 = tile1, tile2 = tile2 )
  
  # convenience method for creation
  @classmethod
  def create_with_tile_chars( cls, tile_char1, tile_char2 ):
    return PGHand.create( PGTile.with_char( tile_char1), PGTile.with_char( tile_char2 ) )
  
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
      return self.high_tile_beats( other )          # same value, return tile comparison
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
    
# run the test when invoked as a test (this is boilerplate
# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()

