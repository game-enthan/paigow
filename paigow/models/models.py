# This file defines the python objects that correspond to
# database tables, for the paigow321 game.  Defining them here
# gets them defined for the database and allows python methods
# to work with the database.

from mainsite.settings import STATIC_URL

from django.db import models

from pgtile   import PGTile
from pggame   import PGGame
from pgplayer import PGPlayer


# ----------------------------------------------------
# This 'through' table represents the player's status
# in any game (s)he's played in or is still playing in.

class PGPlayerInGame(models.Model):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'
  
  # What it prints out
  def __unicode__( self ):
    return "pig: " + str( self.player ) + " in " + str( self.game )

  # The 'through' fields, so we can find, from a game,
  # all the players in a game.
  player = models.ForeignKey(PGPlayer)
  game = models.ForeignKey(PGGame)
  
  # The number of points this player has scored so far
  # in this game.
  player_score = models.IntegerField() 
  
  # If the player has set their tiles, these are the
  # hands they've set.
  set1 = models.CharField( max_length = 4 );
  set2 = models.CharField( max_length = 4 );
  set3 = models.CharField( max_length = 4 );
  
  # allow creation with default fields
  @classmethod
  def create( cls, game, player ):
    return cls( 
      game = game,
      player = player,
      deal_state = PGPlayerInGame.NOT_READY,
      set1 = "    ",
      set2 = "    ",
      set3 = "    ",
      player_score = 0 )

  # The current state of this player in this particular deal.
  # He has already seen his hand, and may be still trying to
  # set tiles, or may have finished and is waiting for the
  # others to set their tiles.
  NOT_READY  =      'NO'    # the player has not yet requested
                            # his tiles for this deal (i.e. the
                            # deal is ready but the browser request
                            # for this game, from this player, has
                            # not yet been made).
  SETTING_TILES =   'ST'    # the player is still setting tile
  PREVIEW_HANDS =   'PH'    # the player is previewing his hands
  READY =           'RD'    # the player has set the tiles
  
  DEAL_STATE_CHOICES = ( 
    ( NOT_READY,    'Not yet seated' ),
    ( SETTING_TILES,    'Setting tiles' ),
    ( PREVIEW_HANDS,    'Previwing hands' ),
    ( READY,  'Tiles have been set' ),
  )
  deal_state = models.CharField(
    max_length = 2,
    choices = DEAL_STATE_CHOICES,
    default = NOT_READY )
  
  def score( self ):
    return self.player_score
  
  def add_to_score( self, new_points ):
    self.score += new_points
    save()
  
  def state( self ):
    return self.deal_state
  
  def sets( self ):
    from paigow.pgset import PGSet
    return [ PGSet.create_with_tile_chars(self.set1), PGSet.create_with_tile_chars(self.set2), PGSet.create_with_tile_chars(self.set3) ]
  
  # player has been dealt sets, remember these when they set it
  def set_dealt_sets( self, sets ):
    self.set1 = sets[0].tile_chars()
    self.set2 = sets[1].tile_chars()
    self.set3 = sets[2].tile_chars()
    self.save()
  
  def player_is_previewing_hands( self ):
    self.deal_state = PGPlayerInGame.PREVIEW_HANDS
    self.save()
    
  def player_has_unpreviewed_hands( self ):
    self.deal_state = PGPlayerInGame.SETTING_TILES
    self.save()
    
  def tiles_were_requested( self ):
    if ( self.deal_state == PGPlayerInGame.NOT_READY ):
      self.deal_state = PGPlayerInGame.SETTING_TILES
      self.save()
  
  def player_is_ready( self, set1, set2, set3 ):
    from paigow.pgset import PGSet
    if PGSet.create_with_tile_chars( self.set1 ).can_be_rearranged_to( set1 ):
      self.set1 = set1
    if PGSet.create_with_tile_chars( self.set2 ).can_be_rearranged_to( set2 ):
      self.set2 = set2
    if PGSet.create_with_tile_chars( self.set3 ).can_be_rearranged_to( set3 ):
      self.set3 = set3
    self.deal_state = PGPlayerInGame.READY
    self.save()

