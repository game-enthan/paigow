# This file defines the python objects that correspond to
# database tables, for the paigow321 game.  Defining them here
# gets them defined for the database and allows python methods
# to work with the database.

from mainsite.settings import STATIC_URL

from django.db import models

# 'models' is a package, or bundle, that contains a bunch of
# python classes that are connected to the underlying database.
# django.db is the overarching django group of packages that
# contain the 'models' class.
#
# 'models.Model' is a class that represents one table in the
# relational database underlying these models.
#
# 'models.XXXField' is a class that represents one column in
# the table it's within.

# As an example:
#
#      class Thing(models.Model)
#        name = models.CharField
#
#  means that the database has a table named 'Thing', and that
# table has a single CHAR column named 'name'.

# these imports don't actually do anything but it's nice to
# know where the various tables are defined
from pgtile import PGTile
from pggame import PGGame

# Since we are in a 'models' directory with __init.py__ also
# in that directory, python treats us as if we were all in a
# class called 'models'.  This causes the django DB infra-
# structure to automatically prepend "models_" to the database
# table; that causes a lot of issues.  Meta:app_label is the
# variable within the class that django's DB stuff looks at,
# so we override it with our app's name without 'model' in it.
# This is why this is in each model:
#    class Meta:
#      app_label = 'paigow'


# ----------------------------------------------------
# This represents one player, there can be any number

class PGPlayer(models.Model):

  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'

  name = models.CharField(max_length=50)
  
  # This will make the object return value print out as
  # the name of the tile.
  def __unicode__(self):
    return self.name





# ----------------------------------------------------
# This 'through' table represents the player's status
# in any game (s)he's played in or is still playing in.

class PGPlayerInGame(models.Model):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'

  # The 'through' fields, so we can find, from a game,
  # all the players in a game.
  player_id = models.ForeignKey(PGPlayer)
  game_id = models.ForeignKey(PGGame)
  
  # The current status in that game: the score could'
  # have been a PositiveIntegerField but let's allow
  # for future games where we can have negative scores.
  score = models.IntegerField()



# ----------------------------------------------------
# This 'join' table represents one tile within a
# given deal  By finding all the tiles in one
# game, for one deal_index, and looking at their
# position in the deck, we can figure out the ordering
# of the tiles and from there, using the same dealing
# function, re-play that deal.

class PGTileInDeal(models.Model):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'

  # The 'join' table of the deck after shuffling, before
  # dealing.  We assume that a deal, for any given game
  # and set of players, can be replayed with exactly the
  # same results.  Therefore we only need the initial state
  # to represent what each player has in the deal.
  # The constraint that the to-many has to include every tile
  # exactly once should be implemented in the code.
  # We could have used a number from 1..32! to represent
  # every possible deal, but the 32 tiles in the deck give us
  # 263,130,836,933,693,530,167,218,012,160,000,000
  # different possibilities; a quick calculation shows we
  # need 82 bits to represent that.  Not worth doing.
  tile_id = models.ForeignKey(PGTile)
  game_id = models.ForeignKey(PGGame)
  
  # Which deal this is for, in that game.  By enumerating
  # through this table for a given game, and getting each
  # tile for each deal, we can replay the deals of a game.
  deal_number = models.PositiveSmallIntegerField()
  
  # Where it is in the deck; we could make sure we use
  # ORDER BY ID in the table, but let's make it explicit.
  position = models.PositiveSmallIntegerField()
  



