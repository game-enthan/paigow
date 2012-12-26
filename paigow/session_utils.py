from models.pgplayer import PGPlayer

#-------------------------------------------------------------------
# convenience
# return the PGPlayer with the current request session id
def session_player( request ):
  if 'player_id' in request.session:
    return PGPlayer.with_id( request.session['player_id'] )
  else:
    return None

