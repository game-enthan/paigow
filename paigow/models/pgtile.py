# This file defines the PGTile python class, derived from the
# django 'models.Model' class that relates python classes to
# relational database tables.

from django.db import models

# since we are in a 'models' directory with __init.py__ also
# in that directory, python treats us as if we were all in a
# class called 'models'.  This causes the django DB infra-
# structure to automatically prepend "models_" to the database
# table; that causes a lot of issues.  Meta:app_label is the
# variable within the class that django's DB stuff looks at,
# so we override it with our app's name without 'model' in it.
# This is why this is in each model:
#    class Meta:
#      app_label = 'paigow'

# This represents one tile; this table never change and
# is pre-populated with the standard Pai Gow deck.  Although
# most of the fields could be computed at runtime from
# the name ("high four"), they are precalculated for
# speed.

class PGTile( models.Model ):

  # since we are in a 'models' directory with __init.py__ also
  # in that directory, python treats us as if we were all in a
  # class called 'models'.  This causes the django DB infra-
  # structure to automatically prepend "models_" to the database
  # table; that causes a lot of issues.  Meta:app_label is the
  # variable to 
  class Meta:
    app_label = 'paigow'
  
  # ----------------------------------------------------------
  # database columns
  
  # Be nice to have a picture too: probably an image
  # whose file name matches this name.
  name = models.CharField( max_length = 30 )
  
  # Each tile has a unique single char value for
  # compact communication
  tile_char = models.CharField( max_length = 1)
  
  # Rank of the tile and its pair: 15:highest, 0:lowest;
  # I think it's save to assume that POSITIVE SMALL INTEGER
  # is still large enough to represent 15 ;)
  tile_rank = models.PositiveSmallIntegerField()
  pair_rank = models.PositiveSmallIntegerField()
  
  # Numerical value.  Both Gee Joon tiles have a
  # value of '3' -- and no other tiles do -- so that
  # value is treated specially in the code that
  # knows it may be 6 as well.
  tile_value = models.PositiveSmallIntegerField()
  
  # The picture is a CSS sprite of an image of all the
  # tiles: this is the x, y of the top-left of the sprite
  # in pixels.  Note we negate this to move the background
  # into position.
  # sprite_left = models.PositiveSmallIntegerField( default = 0 )
  # sprite_top = models.PositiveSmallIntegerField( default = 0 )

  dot_sequence = models.CharField( max_length = 2 )
  
  # ----------------------------------------------------------
  # methods
  
  # This will make the object return value print out as
  # the name of the tile.
  def __unicode__( self ):
    return self.name
  def __str__( self ):
    return unicode(self).encode('utf-8')  # return the four-char string for the tiles
  
  # internal function to return a given filter
  @classmethod
  def get_tiles_matching( cls, filter, is_first = True ):
    # get the tile
    tiles = PGTile.objects.filter( **filter )
    # sanity check(s)
    if not tiles:
      return None
    if ( len(tiles) != 2 ):
      return None
    # there are two of every rank, client can specify which    
    if is_first:
      return tiles[0]
    else:
      return tiles[1]
  
  # return the background-sprite css value for background-position.
  # def background_position_css_value( self, tile_size ):
  #   divisor = 1.0
  #   if ( tile_size == "medium" ):
  #     divisor = 2.0
  #   elif ( tile_size == "small" ):
  #     divisor = 4.0
  #   ret_val = "-" + str(self.sprite_left/divisor) + "px -" + str(self.sprite_top/divisor) + "px"
  #   return ret_val
  
  # return the tile with the given rank, taking into account whether
  # or not it's the first one.
  @classmethod
  def with_rank( cls, rank, is_first = True ):
    return cls.get_tiles_matching( { 'tile_rank': rank }, is_first )
  
  # return the tile with the given char
  @classmethod
  def with_char( cls, tile_char ):
    return cls.objects.get( tile_char__exact = tile_char )
  
  # return a blank tile (not saved in database)
  @classmethod
  def blank_tile( cls ):
    return PGTile( tile_char = ' ', tile_rank = 99, pair_rank = 99, tile_value = 99, sprite_left = 0, sprite_top = 0 )

  def dots( self ):
    from paigow.pgdot import PGDot
    return PGDot.all_dots( self.dot_sequence )
  
  # convenience to allow creation of tiles by name.
  # * double-underscore means that what follows is an
  #   adjustment of the field, so below it will query
  #   based on the 'name' field.
  # * 'exact' is the adjustment that does the query by
  #   full string matching rather than substring match
  # * 'i' prefix means case-insensitive
  @classmethod
  def with_name( cls, name, is_first = True ):
    return cls.get_tiles_matching( { 'name__iexact': name }, is_first )
  
  def is_teen_or_day( self ):
    return self.name == "teen" or self.name == "day"
  
  def is_gee_joon_tile( self ):
    return self.name == "gee joon"
  
  def value_is_in( self, values ):
    for value in values:
      if value == self.tile_value:
        return True
    return False
  
  # for compact communication, each tile has a unique letter representing it.
  def char( self ):
    return self.tile_char
  
  # for comparing tiles in the game
  def beats( self, other ):
    return self.tile_rank > other.tile_rank
  
  def is_beaten_by( self, other ):
    return self.tile_rank < other.tile_rank
  
  def copies( self, other ):
    return self.tile_rank == other.tile_rank

  # overload the math when comparing tiles
  #   def __lt__( self, other ):
  #     return self.tile_rank < other.tile_rank
  #   def __le__( self, other ):
  #     return self.tile_rank <= other.tile_rank
  #   def __eq__( self, other ):
  #     return self.tile_rank == other.tile_rank
  #   def __ne__( self, other ):
  #     return self.tile_rank != other.tile_rank
  #   def __ge__( self, other ):
  #     return self.tile_rank >= other.tile_rank
  #   def __gt__( self, other ):
  #     return self.tile_rank > other.tile_rank
  
  
  @classmethod
  def get_shuffled_tiles( self ):
    import random
    all_tiles = list(PGTile.objects.all())
    random.shuffle( all_tiles )
    random.shuffle( all_tiles )
    random.shuffle( all_tiles )
    return all_tiles
  
  
# ----------------------------------------------------
# Test PGTile class

from django.test import TestCase

class PGTileTest(TestCase):
  
  fixtures = [ 'pgtile.json', ]
  
  def test_fixtures( self ):
    self.assertEquals( PGTile.objects.all().count(), 32 )
  
  def test_shuffle( self ):
    shuffled_tiles = PGTile.get_shuffled_tiles();
    self.assertEqual( len( shuffled_tiles ), 32 );
  
  def test_math( self ):
    tile_high = PGTile.with_name( "high ten" )
    tile_low = PGTile.with_name( "mixed nine", True )
    tile_test = PGTile.with_name( "mixed nine", False )
    self.assertTrue( tile_high.beats(tile_low) )
    self.assertFalse( tile_high.is_beaten_by(tile_low) )
    self.assertFalse( tile_low.beats(tile_high) )
    self.assertFalse( tile_low.beats(tile_test) )
    self.assertTrue( tile_low.copies(tile_test) )
    self.assertFalse( tile_low.is_beaten_by(tile_test) )
  
  def test_with_rank( self ):
    tile1 = PGTile.with_rank( 5, True )
    tile2 = PGTile.with_rank( 5, False )
    self.assertTrue( tile1.copies(tile2) )
    tile2 = PGTile.with_rank( 6, True )
    self.assertFalse( tile1.copies(tile2) )
    tile2 = PGTile.with_rank( -1 )
    self.assertIsNone( tile2 )
  
  def test_with_name( self ):
    tile1 = PGTile.with_name( "mixed seven", True )
    self.assertIsNotNone( tile1 )
    tile2 = PGTile.with_name( "Mixed Seven", False )
    self.assertIsNotNone( tile2 )
    self.assertTrue( tile1.copies(tile2) )
    tile2 = PGTile.with_name( "high ten", True )
    self.assertFalse( tile1.copies(tile2) )
    tile2 = PGTile.with_name( "whatever" )
    self.assertIsNone( tile2 )
  
  def test_shuffle( self ):
    shuffled_tiles = PGTile.get_shuffled_tiles()
    self.assertEqual( len(shuffled_tiles), 32 )
  
  def test_is_teen_or_day( self ):
    tile = PGTile.with_name( "harmony four" )
    self.assertFalse( tile.is_teen_or_day() )
    tile = PGTile.with_name( "teen" )
    self.assertTrue( tile.is_teen_or_day() )
    tile = PGTile.with_name( "day" )
    self.assertTrue( tile.is_teen_or_day() )
  
  def test_with_char( self ):
    tile1 = PGTile.with_char( "A" )
    tile2 = PGTile.with_char( "a" )
    tile3 = PGTile.with_char( "b" )
    self.assertTrue( tile1.copies(tile2) )
    self.assertFalse( tile1.copies(tile3) )
  
  # def test_sprite_values( self ):
  #   tile1 = PGTile.with_name( "teen" )
  #   self.assertEqual( tile1.background_position_css_value("large"), "-0.0px -250.0px" )
  #   self.assertEqual( tile1.background_position_css_value("medium"), "-0.0px -125.0px" )

  def test_dot_sequences( self ):
    tile1 = PGTile.with_name( "teen" )
    self.assertEqual( tile1.dot_sequence, "gn" )

  def test_dots( self ):
    tile1 = PGTile.with_name( "teen" )
    self.assertEqual( len( tile1.dots() ), 12 )    

# run the test when invoked as a test (this is boilerplate
# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()
