# This file defines the Tile python class, derived from the
# django 'models.Model' class that relates python classes to
# relational database tables.

from django.db import models

# TBD: these should be in some views class: model shouldn't
# know about how big the images are.

TILE_IMAGE_WIDTH = "100"
TILE_IMAGE_HEIGHT = "250"

# This represents one tile; this table never change and
# is pre-populated with the standard Pai Gow deck.  Although
# most of the fields could be computed at runtime from
# the name ("high four"), they are precalculated for
# speed.

class Tile(models.Model):

  # ----------------------------------------------------------
  # database columns
  
  # Be nice to have a picture too: probably an image
  # whose file name matches this name.
  name = models.CharField(max_length=30)
  
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
  sprite_left = models.PositiveSmallIntegerField()
  sprite_top = models.PositiveSmallIntegerField()
  
  
  # ----------------------------------------------------------
  # methods
  
  
  # This will make the object return value print out as
  # the name of the tile.
  def __unicode__(self):
    return self.name
  
