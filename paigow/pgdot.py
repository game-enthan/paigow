# This file defines the PGDot python class.
#
# A 'dot' decribes the relative location and color of dots
# on a tile.  The paigow tiles are a mix of two halves, and
# each pattern on a half is represented by the following
# letters (thus a tile has two letters):
#
# (a) single red dot on top: red 2
# (b) four red dots on top: red 1, 3, 7, 8
# (c) two white dots on top: white 1, 3
# (d) three white dots on top: white 3, 5, 7
# (e) five white dots on top: white 1, 3, 5, 7, 8
# (f) six white dots on top: white 1, 3, 4, 6, 9, 10
# (g) mixed six dots on top: white 1, 4, 9; red 3, 6, 10
# (h) single red dot on bottom: red 19
# (i) four red dots on bottom: red 13, 14, 18, 20
# (j) two white dots on bottom: white 18, 20
# (k) three white dots on bottom 11, 16, 20
# (l) five white dots on bottom: white 11, 12, 16, 18, 20
# (m) six white dots on bottom: white 11, 12, 15, 17, 18, 20
# (n) mixed six dots on bottom: white 1, 15, 18; red 12, 17, 20

# gee joon: ch, bj
# teen: gn
# day: ah
# high eight: bi
# harmony four: ak
# high ten: el
# long six: dk
# low four: cj
# eleven: fl
# low ten: bm
# high seven: am
# low six: al
# mixed nine: bl, dm
# mixed eight: dl, cm
# mixed seven: bk, cl
# mixed five: bh, ck

# these are the red and white locations of all the dots for
# each of the sequences. Each letter implies a set of red
# dot locations (by number) and a set of white dot locations
# (by number), in two lists.
s_dot_codes = {
  'a': { 'red': [2], 'white': [] },
  'b': { 'red': [1,3,7,8], 'white': [] },
  'c': { 'red': [], 'white': [1,3] },
  'd': { 'red': [], 'white': [3,5,9] },
  'e': { 'red': [], 'white': [1,3,5,9,10] },
  'f': { 'red': [], 'white': [1,3,4,6,9,10] },
  'g': { 'red': [1,4,9], 'white': [3,6,10] },
  'h': { 'red': [19], 'white': [] },
  'i': { 'red': [13,14,18,20], 'white': [] },
  'j': { 'red': [], 'white': [18,20] },
  'k': { 'red': [], 'white': [12,16,18] },
  'l': { 'red': [], 'white': [11,12,16,18,20] },
  'm': { 'red': [], 'white': [11,12,15,17,18,20] },
  'n': { 'red': [12,17,20], 'white': [11,15,18] },
}

# the above dot numbers indicate locations for the dots.
# this is the array for the locations [top, left].
# TBD: these are for medium tiles.  We need to make them
# some sort of percentage.
s_dot_locations = [
  [  0,  0 ],   # placeholder: dots start at one
  [  4,  6 ],
  [  4, 17 ],
  [  4, 28 ],
  [ 24,  6 ],
  [ 24, 17 ],
  [ 24, 28 ],
  [ 34,  6 ],
  [ 34, 28 ],
  [ 44,  6 ],
  [ 44, 28 ],
  [ 64,  6 ],
  [ 64, 28 ],
  [ 74,  6 ],
  [ 74, 28 ],
  [ 84,  6 ],
  [ 84, 17 ],
  [ 84, 28 ],
  [104,  6 ],
  [104, 17 ],
  [104, 28 ],
]

class PGDot:

  def __init__( self, index, color ):
    self.index = index
    self.color = color

  @classmethod
  def sequence( cls, ch_code, color ):
    sequences = s_dot_codes[ch_code]
    if not sequences:
      return []
    return sequences[color]

  @classmethod
  def half_dots( cls, ch_code ):
    ret = []
    red_sequence = PGDot.sequence( ch_code, 'red' )
    white_sequence = PGDot.sequence( ch_code, 'white' )
    for code in red_sequence:
      ret.append( PGDot( code, 'red' ) )
    for code in white_sequence:
      ret.append( PGDot( code, 'white' ) )
    return ret

  @classmethod
  def all_dots( cls, ch_chars ):
    seq0 = PGDot.half_dots( ch_chars[0] )
    seq1 = PGDot.half_dots( ch_chars[1] )
    return seq0 + seq1

  def dict( self ):
    return { 'index': self.index, 'color': self.color }

from django.test import TestCase

class PGDotTest( TestCase ):

  def test_sequence( self ):
    seq = PGDot.sequence( 'j', 'white' )
    self.assertEqual( seq, [18,20] )

  def test_half_dots( self ):
    dots = PGDot.half_dots( 'a' )
    self.assertEqual( len(dots), 1 )
    self.assertEqual( dots[0].color, 'red' )

  def test_all_dots( self ):
    dots = PGDot.all_dots( 'gn' )
    self.assertEqual( len(dots), 12 )
