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
# return the PGPlayerInDeal with the current request session id
def player_in_session_deal( request, game_id, deal_number ):
  from models import PGPlayerInDeal
  from models import PGGame
  try:
    
    game = PGGame.objects.get( id = game_id )
    player = session_player( request )
    if ( not player ):
      raise ValueError
    return game.player_in_deal( player, deal_number )
  
  except:
    print "Malformed request: no player or pig in session"
  
  return None
  
#-------------------------------------------------------------------
# convenience
# return the single opponent for the player in the game
def session_opponent( request, game, deal_number ):
  
  player = session_player( request )
  if ( not player ):
    print "Malformed request: no player in session"
    raise ValueError
  
  opponent = player.opponent_for_deal( game, deal_number )
  if ( not opponent ):
    print "Malformed request: no opponent for player '" + str( player ) + "' in game '" + str( game ) + "'"
    raise ValueError
  
  return opponent


#-------------------------------------------------------------------
# convenience
# return the opponent's player-in-game only if the game is finished
def opponent_in_session_deal( request, game_id, deal_number ):
  from models import PGPlayerInDeal
  from models import PGGame
  
  # if any of these values don't exist it will raise and we'll return None
  try:
    
    game = PGGame.objects.get( id = game_id )
    player = session_player( request )
    opponent = session_opponent( request, game, deal_number )
    pgpid = game.player_in_deal( player, deal_number )
    if ( not pgpid ):
      print "Malformed request: client is not a player in game '" + str( game ) + "'"
      raise ValueError    
    if ( pgpid.state() != PGPlayerInDeal.READY ):
      print "Malformed request: player '" + str( player ) + "' in game '" + str( game ) + "' is requesting tiles before setting theirs!"
      raise ValueError
    pgpido = game.player_in_deal( opponent, deal_number )
    if ( not pgpido ):
      print "Malformed request: opponent '" + str( opponent ) + "' in game '" + str( game ) + "' is not playing!"
      raise ValueError
    if ( pgpido.state() != PGPlayerInDeal.READY ):
      print "Malformed request: opponent '" + str( opponent ) + "' in game '" + str( game ) + "' has not yet finished setting their tiles!"
    return pgpido
    
  except:
    
    print "Malformed request!"
    return None
