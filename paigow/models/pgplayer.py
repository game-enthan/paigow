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
    
  # return the opponent for this game
  def opponents_for_game( self, game ):
    opponents = []
    players = game.players()
    for player in players:
      if ( player != self ):
        opponents.append( player )
    return opponents
  
  
  # return all the games that this player is part of, ordered by the start
  # date of the games.
  def games( self ):
    from paigow.models import PGPlayerInGame
    pgpigs = PGPlayerInGame.objects.filter( player = self ).order_by('game__start_date')
    for pgpig in pgpigs:
      yield pgpig.game


  # This will make the object return value print out as
  # the name of the tile.
  def __unicode__( self ):
    return self.name

# ----------------------------------------------------
# Test PGPlayer class

from django.test import TestCase

class PGPlayerTest( TestCase ):
  
  fixtures = [ 'pgplayer.json', ]

  def setUp( self ):
    self.test_player = PGPlayer.objects.create( name = 'Rudi' )
    self.test_player.save()

#   def tearDown( self ):
#     <do something here if necessary>
  
  def test_name_is_correct( self ):
    '''Name from our instance object database matches what we put in'''
    self.assertEqual( self.test_player.name, 'Rudi' )
  
  def test_with_id( self ):
    self.assertEqual( PGPlayer.with_id( self.test_player.id ), self.test_player )
  
  def test_all_possible_opponents( self ):
    print len(PGPlayer.objects.all())
    self.assertEqual( len(self.test_player.all_possible_opponents()), 1 ) # computer should be there
    other_guy = PGPlayer.create( "other_guy", "foo@bar.com", "xxx" )
    other_guy.save()
    self.assertEqual( len(self.test_player.all_possible_opponents()), 2 )
    self.assertEqual( len(other_guy.all_possible_opponents()), 2 )
    self.assertNotIn( self.test_player, self.test_player.all_possible_opponents() )
    self.assertIn( other_guy, self.test_player.all_possible_opponents() )
  
  
  def test_games( self ):
    '''Correctly return a game we're in'''
    from pggame import PGGame
    test_game = PGGame.create( "New Game" )
    test_game.save()
    self.assertNotIn( self.test_player, test_game.players() )
    test_game.add_player( self.test_player )
    self.assertIn( self.test_player, test_game.players() )

  def test_opponent( self ):
    '''Correctly return the opponent in a game'''
    from pggame import PGGame
    test_game = PGGame.create( "New Game" )
    test_game.save()
    test_game.add_player( self.test_player )
    self.assertEqual( len(self.test_player.opponents_for_game( test_game )), 0 )
    other_guy = PGPlayer.create( "other_guy", "foo@bar.com", "xxx" )
    other_guy.save()
    test_game.add_player( other_guy )
    self.assertEqual( len(self.test_player.opponents_for_game( test_game )), 1 )
    self.assertEqual( self.test_player.opponents_for_game( test_game )[0], other_guy )
    self.assertEqual( len(other_guy.opponents_for_game( test_game )), 1 )
    self.assertEqual( other_guy.opponents_for_game( test_game )[0], self.test_player )

# run the test in the correct situation; this is boilerplat
# for all modules that have tests, don't try to figure it out.
if __name__ ==  '__main__':
  print "testing!\n"
  unittest.main()


