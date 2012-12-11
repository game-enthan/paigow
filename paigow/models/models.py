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

from pgtile   import PGTile
from pggame   import PGGame
from pgplayer import PGPlayer

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
# This 'through' table represents the player's status
# in any game (s)he's played in or is still playing in.

class PGPlayerInGame(models.Model):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'

  # allow creation with default fields
  @classmethod
  def create( cls, game, player ):
    return cls( 
      game = game,
      player = player,
      score = 0 )

  # The 'through' fields, so we can find, from a game,
  # all the players in a game.
  player = models.ForeignKey(PGPlayer)
  game = models.ForeignKey(PGGame)
  
  # The current status in that game: the score could'
  # have been a PositiveIntegerField but let's allow
  # for future games where we can have negative scores.
  score = models.IntegerField()



