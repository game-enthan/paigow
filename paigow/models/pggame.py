# This file defines the PGGame object that represents a single
# playing of a single game.  It may be ended or in the middle.

# See 'models.py' for documentation on this line
from django.db import models

from django.utils import timezone 
from django.core.exceptions import ObjectDoesNotExist

# ----------------------------------------------------
# This represents one game, which may or may not be complete.
# A game can be paused in the middle and its state will be
# saved in the database.  To do this, we need to reconstruct:
#
#   ( 1 ) the players that are playing this game
#   ( 2 ) the current score for those players
#   ( 3 ) what they're doing ( waiting for a deal? playing tiles? )
#   ( 4 ) the tiles each player is looking at ( if they're playing )
#

class PGGame( models.Model ):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'
  
  # name of the game ( there may be different types of games )
  name = models.CharField( max_length=100 )
  
  # keep track of when the game was started and when it finished;
  # if the finish date is <TBD> then the game is not over
  start_date = models.DateTimeField( 'start date' )
  finish_date = models.DateTimeField( 'finish date', null = True )
  
  # A game can be paused in the middle, and we need to keep enough
  # state that the next time the players log in, they can resume
  # where they left off.  Games consiste of a number of "deals", where
  # a deal is the distribution of tiles to each player after washing.
  #
  # Games can be in any of the following states ( the two-letter codes
  # are stored in the database, and the text descriptions are for viewing
  # the state on a website or app ).
  ABOUT_TO_DEAL =   'BD'    # between deals in an unfinished game; the
                            # game when created is this because it's about
                            # to deal.
  SETTING_TILES =   'ST'    # the tiles have been dealt and at least one
                            # player is still setting tiles
  COMPARING_HANDS = 'CH'    # all players have set their tiles and are
                            # looking at the results
  GAME_OVER =       'GO'    # the game is over
  
  GAME_STATE_CHOICES = ( 
    ( ABOUT_TO_DEAL,    'About to deal' ),
    ( SETTING_TILES,    'Setting tiles' ),
    ( COMPARING_HANDS,  'Checking who has won and lost' ),
    ( GAME_OVER,        'Game over, dude' ),
  )
  game_state = models.CharField(
    max_length = 2,
    choices = GAME_STATE_CHOICES,
    default = ABOUT_TO_DEAL )

  # allow creation with default fields
  @classmethod
  def create( cls, name ):
    return cls( 
      name = name,
      start_date = timezone.now(),
      game_state = PGGame.ABOUT_TO_DEAL,
      current_deal_number = 0 )

  # If the Game is in the middle of a deal when the players have to pause,
  # then in order to resume we need to save enough information that they
  # can get exactly the same tiles in the same order.  We could create a
  # separate table for that, but if we assume that deals to players are
  # always in the same order, then we can just save the original order of
  # the deck and let it re-deal.
  #
  # The database saves every single deal ( deck of tiles after washing ) for
  # every single game, so this game may have a number of deals in the database
  # associated with it.  Each deal for a given game has a unique deal_index
  # ( a small number starting at 1 ) so we can find the specific deal that is
  # currently being played.  This is that number.
  current_deal_number = models.PositiveSmallIntegerField()
  
  # convenience
  @classmethod
  def with_id( cls, game_id ):
    if ( game_id ):
      games = PGGame.objects.filter( id = game_id )
      if ( games.count() > 0 ):
        return games[0]
    return None
  
  # This will make the object return value print out as the name of the game.
  def __unicode__( self ):
    return self.name
  
  def state( self ):
    return self.game_state
  
  # Return the all the players for this single game.  Always order them by
  # player IDs to make sure the list is already returned in the same order.
  def players( self ):
    players = []
    from pgplayerindeal import PGPlayerInDeal
    pigs = PGPlayerInDeal.objects.filter( game = self, deal_number = self.current_deal_number ).order_by( 'player__id' )
    for pgpid_player in pigs:
      players.append( pgpid_player.player )
    return players
  
  # Add a player to this game
  def add_player( self, player ):
    from pgplayer import PGPlayer
    from pgplayerindeal import PGPlayerInDeal
    
    # we can only add players when we have a deal.  If there hasn't been any deal,
    # make one now.  This should only happen when adding the first player.
    if ( self.current_deal_number == 0 ):
      self.deal_tiles()
    
    # We can only add players during the first deal.
    if ( self.current_deal_number != 1 ):
      raise RuntimeError
    
    pgpid_player = PGPlayerInDeal.create( self, player, self.current_deal_number )
    pgpid_player.save()
  
  
  # Get the deal given the deal number
  def deal( self, deal_number ):
    from pgdeal import PGDeal
    deals = PGDeal.objects.filter( game = self, deal_number = deal_number )
    # sanity check: better have only one thing returned
    # TBD: throw exception, resulting in error on page
    if deals and (len(deals) >= 1):
      return deals[0]
    else:
      return None
  
  # Get the current deal
  def current_deal( self ):
    return self.deal( self.current_deal_number )
  
  def player_in_game( self, player ):
    from pgplayerindeal import PGPlayerInDeal
    pigs = PGPlayerInDeal.objects.filter( game = self, player = player, deal_number = self.current_deal_number )
    if ( not pigs ):
      return None
    return pigs[0]
    
  # shuffle the deck and save it as the current deal
  def deal_tiles( self ):
    
    from pgtile import PGTile
    from pgdeal import PGDeal
    
    # We had better be about to deal
    if ( self.game_state != PGGame.ABOUT_TO_DEAL ):
      raise Exception( 'Trying to deal in wrong state!' )
    
    # get a shuffled set of tiles
    tiles = PGTile.get_shuffled_tiles()
    
    # it's a new deal number
    self.current_deal_number += 1
    
    # remember this deal
    deal = PGDeal.create( tiles, self, self.current_deal_number )
    deal.save()
    
    # game is not about to deal anymore
    self.game_state = PGGame.SETTING_TILES
    self.save()
  
  def player_in_deal( self, player, deal_number ):
    from pgplayerindeal import PGPlayerInDeal
    try:
      pgpid = PGPlayerInDeal.objects.get( game = self, player = player, deal_number = deal_number )
      return pgpid
    except:
      print "Cannot get pgpid for player '" + str(player) + "' in game '" + str(self) + "' for deal " + str(deal_number)
      return None
  
  def score_as_of_deal_for_player( self, player, deal_number ):
    from pgplayerindeal import PGPlayerInDeal
    pgpids = PGPlayerInDeal.objects.filter( game = self, player = player )
    score = 0
    for pgpid in pgpids:
      if ( pgpid.deal_number < deal_number ):
        score = score + pgpid.score()
    return score
  
  def score_for_player( self, player ):
    return self.score_as_of_deal_for_player( self, player, self.current_deal_number + 1 )
  
  def sets_for_player( self, player, deal_number ):
    
    from paigow.pgset import PGSet
    from pgplayerindeal import PGPlayerInDeal

    players = self.players()
    
    # TBD: remove assumption that there are only two players.  This
    # decides whether this player gets the first set of tiles or the
    # second set of tiles.
    index = 0
    if ( player != players[0] ):
      index = 1
    
    # Create the hands and fill them.
    deal = self.deal( deal_number )
    sets = []
    for i in range(3):
      set = PGSet.create( ( deal.tile( index ),
                            deal.tile( index + 2 ),
                            deal.tile( index + 4 ),
                            deal.tile( index + 6 ),
                          )
                        )
      sets.append( set )
      index += 8
    
    # remember that this player asked for this deal
    try:
      pgpid_player = PGPlayerInDeal.objects.get( game = self, player = player, deal_number = deal_number )
    except ObjectDoesNotExist:
      pgpid_player = PGPlayerInDeal.create(  self, player, deal_number )
    
    pgpid_player.tiles_were_requested()
    
    # remember what hands were dealt; when it comes time for
    # the player to say how they set, we want to verify that
    # they didn't cheat ;)
    pgpid_player.set_dealt_sets( sets )
    
    return sets
  
  def state_for_player( self, player ):
    from pgplayerindeal import PGPlayerInDeal    
    pgpid_player = self.player_in_deal( player, self.current_deal_number )
    if ( not pgpid_player ):
      raise ValueError
    return pgpid_player.state_ui( pgpid_player.state() )
  
  def player_has_set_his_tiles( self, player ):
    from pgplayerindeal import PGPlayerInDeal
    
    # if we're already finished with the game, don't bother.
    if ( self.game_state != PGGame.SETTING_TILES ):
      return
    
    # if the opponent is not ready, nothing to do
    pgpid_opponent = self.player_in_game( player.opponent_for_game( self ) )
    if not pgpid_opponent:
      raise ValueError
    if ( pgpid_opponent.state() != PGPlayerInDeal.READY ):
      return
    
    # both are ready!  We'are comparing hands, and add the score
    self.game_state = PGGame.COMPARING_HANDS
    self.save()
    
    pgpid_player = self.player_in_game( player )
    if not pgpid_player:
      raise ValueError
    pgpid_player.record_scores_against( pgpid_opponent )
    
      
# ----------------------------------------------------
# Test PGGame class

from django.test import TestCase

class PGGameTest( TestCase ):

  fixtures = [ 'pgtile.json' ]
  
  def setUp( self ):
    # TBD: don't use database, since that makes this an integratino test
    # rather than a unit test.  That may take re-architecting things.
    from pgplayer import PGPlayer
    self.test_game = PGGame.create( 'paigow321' )
    self.test_game.save()
    self.player1 = PGPlayer.objects.create( name = 'Rudi' )
    self.player2 = PGPlayer.objects.create( name = 'Dave' )
    self.test_game.add_player( self.player1 )
    self.test_game.add_player( self.player2 )

#   def tearDown( self ):
#     <do something here if necessary>

  def test_add_player( self ):
    '''Adding two players results in a game with 2 players'''
    from pgplayer import PGPlayer
    self.assertEqual( len(self.test_game.players()), 2 )
    self.assertIn( self.player1, self.test_game.players() )
    self.assertIn( self.player2, self.test_game.players() )

  def test_order_player( self ):
    '''Adding two players in any order always returns them in the same order'''
    from pgplayer import PGPlayer
    players1 = self.test_game.players()
    game2 = PGGame.create( 'paigow321_2' )
    game2.save()
    game2.add_player( self.player2 )
    game2.add_player( self.player1 )
    players2 = game2.players()
    self.assertEqual( players1[0], players2[0] )
    self.assertEqual( players1[1], players2[1] )

  def test_deal( self ):
    from pgdeal import PGDeal
    self.assertEqual( self.test_game.current_deal_number, 1 )
    tiles_in_deal = PGDeal.objects.filter( game = self.test_game, deal_number = 1 )
    self.assertEqual( tiles_in_deal.count(), 1 )
  
  def test_sets_for_player( self ):
    from paigow.pgset import PGSet
    from pgplayer import PGPlayer
    from pgplayerindeal import PGPlayerInDeal
    sets = self.test_game.sets_for_player( self.player1, self.test_game.current_deal_number )
    self.assertEqual( len(sets), 3 )
    sets = self.test_game.sets_for_player( self.player2, self.test_game.current_deal_number )
    self.assertEqual( len(sets), 3 )


# run the test when invoked as a test (this is boilerplate
# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()


