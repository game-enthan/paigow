# This file defines the python objects that correspond to
# database tables, for the paigow321 game.  Defining them here
# gets them defined for the database and allows python methods
# to work with the database.

# These statements allow this file to know what certain classes
# for subclassing.
#import datetime
#from django.utils import timezone

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


# ----------------------------------------------------
# This represents one tile; this table never change and
# is pre-populated with the standard Pai Gow deck.  Although
# most of the fields could be computed at runtime from
# the name ("high four"), they are precalculated for
# speed.
class Tile(models.Model):

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
  
  # This will make the object return value print out as
  # the name of the tile.
  def __unicode__(self):
    return self.name
  


# ----------------------------------------------------
# This represents one player, there can be any number

class Player(models.Model):
  name = models.CharField(max_length=50)
  
  # This will make the object return value print out as
  # the name of the tile.
  def __unicode__(self):
    return self.name



# ----------------------------------------------------
# This represents one game, which may or may not be complete.
# A game can be paused in the middle and its state will be
# saved in the database.  To do this, we need to reconstruct:
#
#   (1) the players that are playing this game
#   (2) the current score for those players
#   (3) what they're doing (waiting for a deal? playing tiles?)
#   (4) the tiles each player is looking at (if they're playing)
#

class Game(models.Model):
  
  # name of the game (there may be different types of games)
  name = models.CharField(max_length=100)
  
  # keep track of when the game was started and when it finished;
  # if the finish date is <TBD> then the game is not over
  start_date = models.DateTimeField('start date')
  finish_date = models.DateTimeField('start date')
  
  # A game can be paused in the middle, and we need to keep enough
  # state that the next time the players log in, they can resume
  # where they left off.  Games consiste of a number of "deals", where
  # a deal is the distribution of tiles to each player after washing.
  #
  # Games can be in any of the following states (the two-letter codes
  # are stored in the database, and the text descriptions are for viewing
  # the state on a website or app).
  ABOUT_TO_DEAL =   'BD'   # between deals in an unfinished game; the
                           # game when created is this because it's about
                           # to deal.
  GAME_OVER =       'GO'   # the game is over
  PLAYING =         'PL'   # the players are playing the deal
  
  GAME_STATE_CHOICES = (
    ( ABOUT_TO_DEAL, 'About to deal' ),
    ( PLAYING,       'Playing the tiles' ),
    ( GAME_OVER,     'Game over, dude' ),
  )
  game_state = models.CharField(max_length=2,
                        choices=GAME_STATE_CHOICES,
                        default=ABOUT_TO_DEAL)

  # If the Game is in the middle of a deal when the players have to pause,
  # then in order to resume we need to save enough information that they
  # can get exactly the same tiles in the same order.  We could create a
  # separate table for that, but if we assume that deals to players are
  # always in the same order, then we can just save the original order of
  # the deck and let it re-deal.
  #
  # The database saves every single deal (deck of tiles after washing) for
  # every single game, so this game may have a number of deals in the database
  # associated with it.  Each deal for a given game has a unique deal_index
  # (a small number starting at 1) so we can find the specific deal that is
  # currently being played.  This is that number.
  deal_number = models.PositiveSmallIntegerField()
  
  # This will make the object return value print out as the name of the game.
  def __unicode__(self):
    return self.name



# ----------------------------------------------------
# This 'through' table represents the player's status
# in any game (s)he's played in or is still playing in.

class PlayerInGame(models.Model):
  
  # The 'through' fields, so we can find, from a game,
  # all the players in a game.
  player = models.ForeignKey(Player)
  game = models.ForeignKey(Game)
  
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

class TileInDeal(models.Model):
  
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
  tile = models.ForeignKey(Tile)
  game = models.ForeignKey(Game)
  
  # Which deal this is for, in that game.  By enumerating
  # through this table for a given game, and getting each
  # tile for each deal, we can replay the deals of a game.
  deal_number = models.PositiveSmallIntegerField()
  
  # Where it is in the deck; we could make sure we use
  # ORDER BY ID in the table, but let's make it explicit.
  position = models.PositiveSmallIntegerField()
  



