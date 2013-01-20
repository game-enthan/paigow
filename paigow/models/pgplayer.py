# This file defines the PGPlayer object that represents a single
# player who can play in any number of games.

# See 'models.py' for documentation on this line
from django.db import models

# ----------------------------------------------------
# This represents one player, there can be any number

class PGPlayer( models.Model ):
  
  # make sure the DB table name is what we want
  class Meta:
    app_label = 'paigow'
  
  name = models.CharField( max_length = 50 )
  email = models.CharField( max_length = 100 )
  password = models.CharField( max_length = 100 )
  
  # This will make the object return value print out as
  # the name of the tile.
  def __unicode__( self ):
    return self.name
  
  # convenience to create so we don't have to create a dictionary
  @classmethod
  def create( cls, name, email, password ):
    return cls( 
      name = name,
      email = email,
      password = password )
  
  # convenience to get the player with this id
  @classmethod
  def with_id( cls, player_id ):
    if ( player_id ):
      return PGPlayer.objects.get( id = player_id )
    else:
      return None
  
  # convenience to get all players except this id (i.e. all possible opponents).
  def all_possible_opponents( self ):
    return PGPlayer.objects.exclude( id = self.id )
    
  # return the opponent for this deal
  def opponent_for_deal( self, game, deal_number ):
    players = game.players()
    for player in players:
      if ( player != self ):
        return player
    return None
  
  # return the opponent for this game
  def opponent_for_game( self, game ):
    return self.opponent_for_deal( game, 1 )
  
  # return all the games that this player is part of, ordered by the start
  # date of the games.
  def games( self ):
    from pgplayerindeal import PGPlayerInDeal
    pgpigs = PGPlayerInDeal.objects.filter( player = self, deal_number = 1 ).order_by('game__start_date')
    for pgpig in pgpigs:
      yield pgpig.game

  # return all the opponents this player has or is playing against.
  def all_opponents_in_all_games( self ):
    opponents = []
    games = self.games()
    for game in games:
      opponent = self.opponent_for_game( game )
      if not opponent in opponents:
        opponents.append( opponent )
    return opponents
  
  # return all the games for a given opponent
  def games_against_opponent( self, opponent ):
    games = []
    for game in self.games():
      if opponent == self.opponent_for_game( game ):
        games.append( game )
    return games
  
  def record_against_opponent( self, opponent ):
    wins = 0
    losses = 0
    in_progress = 0
    games = self.games_against_opponent( opponent )
    for game in games:
      winner = game.winner()
      if not winner:
        in_progress += 1
      elif winner == self:
        wins += 1
      else:
        losses += 1
    return wins, losses, in_progress

# ----------------------------------------------------
# Test PGPlayer class

from django.test import TestCase

class PGPlayerTest( TestCase ):
  
  fixtures = [ 'pgtile.json', 'pgplayer.json', ]

  def setUp( self ):
    self.test_player = PGPlayer.objects.create( name = 'Rudi' )
    self.test_player.save()
  
  def create_game_for_test( self ):
    from pggame import PGGame
    game = PGGame.create( "New Game" )
    game.save()
    self.assertNotIn( self.test_player, game.players() )
    game.add_player( self.test_player )
    self.assertIn( self.test_player, game.players() )
    return game
  
  def add_opponent_to_game( self, game ):
    other_guy = PGPlayer.create( "other_guy", "foo@bar.com", "xxx" )
    other_guy.save()
    game.add_player( other_guy )
    return other_guy
  
  def test_name_is_correct( self ):
    '''Name from our instance object database matches what we put in'''
    self.assertEqual( self.test_player.name, 'Rudi' )
  
  def test_with_id( self ):
    self.assertEqual( PGPlayer.with_id( self.test_player.id ), self.test_player )
  
  def test_all_possible_opponents( self ):
    self.assertEqual( len(self.test_player.all_possible_opponents()), 1 ) # computer should be there
    other_guy = PGPlayer.create( "other_guy", "foo@bar.com", "xxx" )
    other_guy.save()
    self.assertEqual( len(self.test_player.all_possible_opponents()), 2 )
    self.assertEqual( len(other_guy.all_possible_opponents()), 2 )
    self.assertNotIn( self.test_player, self.test_player.all_possible_opponents() )
    self.assertIn( other_guy, self.test_player.all_possible_opponents() )
  
  
  def test_games( self ):
    '''Correctly return a game we're in'''
    game = self.create_game_for_test()

  def test_opponent( self ):
    '''Correctly return the opponent in a game'''    
    from pggame import PGGame
    game = self.create_game_for_test()
    self.assertIsNone( self.test_player.opponent_for_deal( game, 1 ) )
    other_guy = self.add_opponent_to_game( game )
    self.assertEqual( self.test_player.opponent_for_deal( game, 1 ), other_guy )
    self.assertEqual( other_guy.opponent_for_deal( game, 1 ), self.test_player )
  
  def test_opponents_for_game( self ):
    from pggame import PGGame
    game = self.create_game_for_test()
    opponent = self.add_opponent_to_game( game )
    all_opponents = self.test_player.all_opponents_in_all_games()
    self.assertIn( opponent, all_opponents )
    games_against_opponent = self.test_player.games_against_opponent( opponent )
    self.assertEqual( len( games_against_opponent ), 1 )
    self.assertEqual( games_against_opponent[0], game )
    game2 = self.create_game_for_test()
    opponent2 = self.add_opponent_to_game( game2 )
    all_opponents = self.test_player.all_opponents_in_all_games()
    self.assertEqual( len( all_opponents ), 2 )
    self.assertIn( opponent, all_opponents )
    self.assertIn( opponent2, all_opponents )
    game3 = self.create_game_for_test()
    game3.add_player( opponent )
    all_opponents = self.test_player.all_opponents_in_all_games()
    self.assertEqual( len( all_opponents ), 2 )

# run the test in the correct situation; this is boilerplat
# for all modules that have tests, don't try to figure it out.
if __name__ ==  '__main__':
  unittest.main()

