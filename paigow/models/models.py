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
    self.player_score += new_points
    self.save()
  
  def state( self ):
    return self.deal_state
  
  @classmethod
  def state_ui( cls, state ):
    if ( state == PGPlayerInGame.NOT_READY ):
      return "absent"
    elif ( state == PGPlayerInGame.SETTING_TILES ):
      return "scheming..."
    elif ( state == PGPlayerInGame.PREVIEW_HANDS ):
      return "deciding..."
    elif ( state == PGPlayerInGame.READY ):
      return "tiles are set"
    else:
      raise ValueError
  
  def sets( self ):
    from paigow.pgset import PGSet
    return [ self.set(1), self.set(2), self.set(3) ]
  
  # player has been dealt sets, remember these when they set it
  def set_dealt_sets( self, sets ):
    self.set1 = sets[0].tile_chars()
    self.set2 = sets[1].tile_chars()
    self.set3 = sets[2].tile_chars()
    self.save()
  
  def set( self, set_num ):
    from paigow.pgset import PGSet    
    if set_num == 1:
      pgset = self.set1
    elif set_num == 2:
      pgset = self.set2
    elif set_num == 3:
      pgset = self.set3
    else:
      print "PGPlayerInSet asked for invalid set number " + str( set_num )
      raise ValueError
    return PGSet.create_with_tile_chars( pgset )
  
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
  
  def which_set_is_this( self, test_set ):
    from paigow.pgset import PGSet
    if self.set(1).can_be_rearranged_to( test_set ):
      return 1
    if self.set(2).can_be_rearranged_to( test_set ):
      return 2
    if self.set(3).can_be_rearranged_to( test_set ):
      return 3
    return 0
  
  def player_is_ready( self, set1, set2, set3 ):
    from paigow.pgset import PGSet
    
    # make sure the three hands can be a re-arrangement of the current three hands.
    have_set1 = self.which_set_is_this( set1 )
    have_set2 = self.which_set_is_this( set2 )
    have_set3 = self.which_set_is_this( set3 )
    if (have_set1 != have_set2) and (have_set1 != have_set3) and (have_set2 != have_set3):
      self.set1 = set1
      self.set2 = set2
      self.set3 = set3
      self.deal_state = PGPlayerInGame.READY
      self.save()
      self.game.player_has_set_his_tiles( self.player )
    else:
      print "Player " + str( self.player) + " is ready in game " + str( self.game ) + " but the sets do not compute!"
  
  def background_position_css_value( self, pgtile_size ):
    from paigow.pgset import PGSet
    ret_val = "|"
    sets = self.sets()
    for pgset in sets:
      for tile in pgset.tiles:
        ret_val += tile.background_position_css_value( pgtile_size ) + ";"
      ret_val += "|"
    return ret_val
  
  def win_lose_string_against( self, pigo ):
    # only do it if both are ready.
    if ( self.state() != PGPlayerInGame.READY or pigo.state() != PGPlayerInGame.READY ):
      raise ValueError
    
    # for each set, return W for win, . for push and L for loss
    ret_val = ""
    player_sets = self.sets()
    opponent_sets = pigo.sets()
    for player_set, opponent_set in zip(player_sets, opponent_sets):
      if ( player_set > opponent_set ):
        ret_val += "W"
      elif ( player_set < opponent_set):
        ret_val += "L"
      else:
        ret_val += "."
    return ret_val
  
  def record_score_char_for_set( self, pigo, ch, num_points ):
    if ch == 'W':
      self.add_to_score( num_points )
    elif ch == 'L':
      pigo.add_to_score( num_points )
  
  def record_scores_against( self, pigo ):
    wl_str = self.win_lose_string_against( pigo )
    num_points = 3
    for ch in wl_str:
      self.record_score_char_for_set( pigo, ch, num_points )
      num_points = num_points - 1
