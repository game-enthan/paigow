from models.pgplayer import PGPlayer

#-------------------------------------------------------------------
# convenience
# return the PGPlayer with the current request session id
def session_player( request ):
  if 'player_id' in request.session:
    return PGPlayer.with_id( request.session['player_id'] )
  else:
    return None

#-------------------------------------------------------------------
# convenience
# return the single opponent for the player in the game
def session_opponent( request, game ):
  
  player = session_player( request )
  if ( not player ):
    print "Malformed request: no player in session"
    raise ValueError
  
  opponents = player.opponents_for_game( game )
  if ( not opponents ):
    print "Malformed request: no opponents for player '" + str( player ) + "' in game '" + str( game ) + "'"
    raise ValueError
  
  opponent = opponents[0]
  if ( not opponent ):
    print "Malformed request: no first opponent for player '" + str( player ) + "' in game '" + str( game ) + "'"
    raise ValueError
  
  return opponent


#-------------------------------------------------------------------
# convenience
# return the opponent's player-in-game only if the game is finished
def opponent_in_session_game( request, game_id ):
  from models import PGPlayerInGame
  from models import PGGame
  
  # if any of these values don't exist it will raise and we'll return None
  try:
    
    game = PGGame.objects.get( id = game_id )
    player = session_player( request )
    opponent = session_opponent( request, game )
    pig = game.player_in_game( player )
    if ( not pig ):
      print "Malformed request: client is not a player in game '" + str( game ) + "'"
      raise ValueError    
    if ( pig.state() != PGPlayerInGame.READY ):
      print "Malformed request: player '" + str( player ) + "' in game '" + str( game ) + "' is requesting tiles before setting theirs!"
      raise ValueError
    pigo = game.player_in_game( opponent )
    if ( not pigo ):
      print "Malformed request: opponent '" + str( opponent ) + "' in game '" + str( game ) + "' is not playing!"
      raise ValueError
    if ( pigo.state() != PGPlayerInGame.READY ):
      print "Malformed request: opponent '" + str( opponent ) + "' in game '" + str( game ) + "' has not yet finished setting their tiles!"
    return pigo
    
  except:
    
    print "Malformed request!"
    return None
