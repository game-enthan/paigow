# This file defines the state of a single player, in a single game,
# during a single deal of the tiles.

from django.db import models

from pgtile   import PGTile
from pggame   import PGGame
from pgplayer import PGPlayer


# ----------------------------------------------------
# This table represents the player's status for a specific
# deal of tiles in a game.  Each time the tiles are dealt
# so the two players can play against each other, two of
# these are created.  The final game will have any number
# of these: one per deal per player.

class PGPlayerInDeal(models.Model):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'
  
  # What it prints out
  def __unicode__( self ):
    return "PGPlayerInDeal: deal number" + str( self.deal_number ) + " for player " + str( self.player ) + " in " + str( self.game )

  # This is the game and the player and the deal number, used to
  # get the player's state for this deal for this game.
  player = models.ForeignKey(PGPlayer)
  game = models.ForeignKey(PGGame)
  deal_number = models.PositiveSmallIntegerField()
  
  # The number of points this player has scored in this deal.
  # If the deal is over, then it is zero.
  player_score = models.IntegerField() 
  
  # If the player has set their tiles, these are the
  # hands they've set.  This will be expressed as a list of sets
  # in the python API.
  set1 = models.CharField( max_length = 4 );
  set2 = models.CharField( max_length = 4 );
  set3 = models.CharField( max_length = 4 );
  
  # allow creation with default fields
  @classmethod
  def create( cls, game, player, deal_number ):
    return cls( 
      game = game,
      player = player,
      deal_number = deal_number,
      deal_state = PGPlayerInDeal.NOT_READY,
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
    if ( state == PGPlayerInDeal.NOT_READY ):
      return "hasn't seen tiles"
    elif ( state == PGPlayerInDeal.SETTING_TILES ):
      return "thinking..."
    elif ( state == PGPlayerInDeal.PREVIEW_HANDS ):
      return "double-checking..."
    elif ( state == PGPlayerInDeal.READY ):
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
    self.deal_state = PGPlayerInDeal.PREVIEW_HANDS
    self.save()
    
  def player_has_unpreviewed_hands( self ):
    self.deal_state = PGPlayerInDeal.SETTING_TILES
    self.save()
    
  def tiles_were_requested( self ):
    if ( self.deal_state == PGPlayerInDeal.NOT_READY ):
      self.deal_state = PGPlayerInDeal.SETTING_TILES
      self.save()
  
  def which_set_is_this( self, test_set_chars ):
    from paigow.pgset import PGSet
    if self.set(1).can_be_rearranged_to( test_set_chars ):
      return 1
    if self.set(2).can_be_rearranged_to( test_set_chars ):
      return 2
    if self.set(3).can_be_rearranged_to( test_set_chars ):
      return 3
    return 0
  
  def player_is_ready( self, set1_chars, set2_chars, set3_chars ):
    from paigow.pgset import PGSet
    
    # make sure the three hands can be a re-arrangement of the current three hands.
    have_set1 = self.which_set_is_this( set1_chars )
    have_set2 = self.which_set_is_this( set2_chars )
    have_set3 = self.which_set_is_this( set3_chars )
    if (have_set1 != 0) and (have_set2 != 0) and (have_set3 != 0) and (have_set1 != have_set2) and (have_set1 != have_set3) and (have_set2 != have_set3):
      self.set1 = set1_chars
      self.set2 = set2_chars
      self.set3 = set3_chars
      self.deal_state = PGPlayerInDeal.READY
      self.save()
      self.game.player_has_set_his_tiles( self.player )
    else:
      #print "Player " + str( self.player) + " is ready in game " + str( self.game ) + " but the sets do not compute!"
      raise ValueError
  
  def background_position_css_value( self, pgtile_size ):
    from paigow.pgset import PGSet
    ret_val = "|"
    sets = self.sets()
    for pgset in sets:
      for tile in pgset.tiles:
        ret_val += tile.background_position_css_value( pgtile_size ) + ";"
      ret_val += "|"
    return ret_val
  
  def win_lose_string_against( self, pgpid_opponent ):
    # only do it if both are ready.
    if ( self.state() != PGPlayerInDeal.READY or pgpid_opponent.state() != PGPlayerInDeal.READY ):
      raise ValueError
    
    # for each set, return W for win, . for push and L for loss
    ret_val = ""
    player_sets = self.sets()
    opponent_sets = pgpid_opponent.sets()
    for player_set, opponent_set in zip(player_sets, opponent_sets):
      if ( player_set > opponent_set ):
        ret_val += "W"
      elif ( player_set < opponent_set):
        ret_val += "L"
      else:
        ret_val += "."
    return ret_val
  
  def record_score_char_for_set( self, pgpid_opponent, ch, num_points ):
    if ch == 'W':
      self.add_to_score( num_points )
    elif ch == 'L':
      pgpid_opponent.add_to_score( num_points )
  
  def record_scores_against( self, pgpid_opponent ):
    wl_str = self.win_lose_string_against( pgpid_opponent )
    num_points = 3
    for ch in wl_str:
      self.record_score_char_for_set( pgpid_opponent, ch, num_points )
      num_points = num_points - 1
    self.save()
    pgpid_opponent.save()

# ----------------------------------------------------
# Test PGPlayerInDeal class

from django.test import TestCase

class PGPlayerInDealTest( TestCase ):

  fixtures = [ 'pgtile.json' ]
  
  game = None
  player = None
  set1 = None
  set2 = None
  set3 = None
  set4 = None

  def setUp( self ):
    from paigow.pgset import PGSet
    self.player = PGPlayer.create( "pidTest", "a@b.com", "xxx" )
    self.player.save()
    self.game = PGGame.create( "test" )
    self.game.save()
    self.set1 = PGSet.create_with_tile_names( ( "teen", "high ten", "day", "high eight" ) )
    self.set2 = PGSet.create_with_tile_names( ( "mixed seven", "mixed five", "harmony four", "teen" ) )
    self.set3 = PGSet.create_with_tile_names( ( "gee joon", "low ten", "mixed eight", "eleven" ) )
    self.set4 = PGSet.create_with_tile_names( ( "gee joon", "low ten", "mixed eight", "high ten" ) )
  
  def test_create( self ):
    pid = PGPlayerInDeal.create( self.game, self.player, 0 )
    self.assertEqual( pid.player, self.player )
    self.assertEqual( pid.game, self.game )
    self.assertEqual( pid.score(), 0 )
    self.assertEqual( pid.deal_number, 0 )
    self.assertEqual( pid.state(), PGPlayerInDeal.NOT_READY )
  
  def test_sets( self ):
    pid = PGPlayerInDeal.create( self.game, self.player, 0 )
    pid.set_dealt_sets( ( self.set1, self.set2, self.set3 ) )
    self.assertEqual( pid.set1, self.set1.tile_chars() )
    self.assertEqual( pid.set2, self.set2.tile_chars() )
    self.assertEqual( pid.set3, self.set3.tile_chars() )
  
  def test_which_set( self ):
    pid = PGPlayerInDeal.create( self.game, self.player, 0 )
    pid.set_dealt_sets( ( self.set1, self.set2, self.set3 ) )
    self.assertEqual( pid.which_set_is_this( self.set1.tile_chars() ), 1 )
    self.assertEqual( pid.which_set_is_this( self.set2.tile_chars() ), 2 )
    self.assertEqual( pid.which_set_is_this( self.set3.tile_chars() ), 3 )
    self.assertEqual( pid.which_set_is_this( self.set4.tile_chars() ), 0 )

  def test_player_is_ready( self ):
    from paigow.pgset import PGSet
    pid = PGPlayerInDeal.create( self.game, self.player, 0 )
    pid.set_dealt_sets( ( self.set1, self.set2, self.set3 ) )    # original sets
    set1new = PGSet.create_with_tile_names( ( "teen", "high eight", "high ten", "day" ) )
    set2new = PGSet.create_with_tile_names( ( "mixed seven", "teen", "mixed five", "harmony four" ) )
    set3new = PGSet.create_with_tile_names( ( "gee joon", "low ten", "mixed eight", "eleven" ) )
    pid.player_is_ready( set1new.tile_chars(), set2new.tile_chars(), set3new.tile_chars() )    # original sets with tiles moved
    self.assertEqual( pid.set1, set1new.tile_chars() )
    self.assertEqual( pid.set2, set2new.tile_chars() )
    self.assertEqual( pid.set3, set3new.tile_chars() )
    pid.player_is_ready( set2new.tile_chars(), set3new.tile_chars(), set1new.tile_chars() )    # re-ordered sets with tiles moved
    self.assertEqual( pid.set1, set2new.tile_chars() )
    self.assertEqual( pid.set2, set3new.tile_chars() )
    self.assertEqual( pid.set3, set1new.tile_chars() )
    self.assertRaises( ValueError, pid.player_is_ready, set2new.tile_chars(), set3new.tile_chars(), self.set4.tile_chars() )    # re-ordered sets with tiles moved, one bad # run the test when invoked as a test (this is boilerplate

# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()


