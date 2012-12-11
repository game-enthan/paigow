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
  
  # return all the games that this player is part of (this returns
  # a generator, which will get evaluated when the caller calls
  # something that needs these values.
  def games( self ):
    from paigow.models import PGPlayerInGame
    pgpigs = PGPlayerInGame.objects.filter( player = self )
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

  def setUp( self ):
    self.test_player = PGPlayer.objects.create( name = 'Rudi' )
    self.test_player.save()

#   def tearDown( self ):
#     <do something here if necessary>

  def test_name_is_correct( self ):
    '''Name from our instance object database matches what we put in'''
    self.assertEqual( self.test_player.name, 'Rudi' )

# run the test in the correct situation; this is boilerplat
# for all modules that have tests, don't try to figure it out.
if __name__ ==  '__main__':
  print "testing!\n"
  unittest.main()


