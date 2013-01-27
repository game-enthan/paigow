# This class implements the strategy for setting tiles and ordering sets.
# It has a bunch of class methods for figuring this out.

# logging.  This must be within a class; when it's a free-standing variable.
# for some reasons setting it to True within the testing class doesn't cause
# it to be true for the calls outside that class.
class PGStrategyLogging:
  logging = False


# Different ways we can auto-set
s_use_numerical_auto_set = False

from paigow.pgset import PGSet

def switch_tiles( set, index1, index2 ):
  temp = set.tiles[index1]
  set.tiles[index1] = set.tiles[index2]
  set.tiles[index2] = temp

def reorder_tiles_within_hands( set ):
  if set.tiles[1].beats( set.tiles[0] ):
    switch_tiles( set, 0, 1 )
  if set.tiles[3].beats( set.tiles[2] ):
    switch_tiles( set, 2, 3 )

def reorder_hands_for_setting( set, ordering ):
  if ordering == 2:
    switch_tiles( set, 1, 2 )
  elif ordering == 3:
    switch_tiles( set, 1, 3 )
  hand1, hand2 = set.hands()
  if ( hand2.beats( hand1 ) ):
    switch_tiles( set, 0, 2 )
    switch_tiles( set, 1, 3 )
  reorder_tiles_within_hands( set )

def choose_ordering( sum1, diff1, sum2, diff2 ):
  if diff1 < diff2:
    return 1
  elif diff2 < diff1:
    return -1
  elif sum1 > sum2:
    return 1
  elif sum2 > sum1:
    return -1
  else:
    return 0

# routines to check if one set has something and the other does not
def which_set_has_it( set1, set2, tst ):
  if tst( set1 ) and not tst( set2 ):
    return 1
  elif tst( set2 ) and not tst( set1 ):
    return 2
  else:
    return None

# take care of special hands
def ordering_for_special_hands( set ):
  if PGStrategyLogging.logging:
    print "\norder for set " + str(set)

  # we'll be moving tiles around; create a temp set.
  loc_set = PGSet.create( set.tiles )
  
  # always use two pairs
  ordering = loc_set.ordering_with_two_pair()
  if PGStrategyLogging.logging:
    print "   order for two pairs " + str(ordering)
  if ordering:
    return ordering
  
  # if we have a pair, there are exceptions
  ordering = loc_set.ordering_with_pair()
  if PGStrategyLogging.logging:
    print "   order for one pairs " + str(ordering)
  if ordering:
    switch_it = False

    # get the tile with the pair
    reorder_hands_for_setting( loc_set, ordering )
    pair_tile = loc_set.tiles[0]
    
    # we never split pairs of 4s, 5s, 10s or 11s
    if pair_tile.tile_value == 4 or \
       pair_tile.tile_value == 5 or \
       pair_tile.tile_value == 10 or \
       pair_tile.tile_value == 11:
      return ordering
    
    # we split teens/days if the other two tiles are both
    # seven or higher
    if pair_tile.is_teen_or_day() and \
       loc_set.tiles[2].tile_value >= 7 and \
       loc_set.tiles[3].tile_value >= 7:
      switch_it = True
    
    # we split nines if the other two are
    # both within (ten, teen, day)
    if pair_tile.tile_value == 9 and \
       ( loc_set.tiles[2].is_teen_or_day() or loc_set.tiles[2].tile_value == 10 ) and \
       ( loc_set.tiles[3].is_teen_or_day() or loc_set.tiles[3].tile_value == 10 ):
      switch_it = True
      
    # we split eights if the other two are
    # both within (elevens, teen, day)
    if pair_tile.tile_value == 8 and \
       ( loc_set.tiles[2].is_teen_or_day() or loc_set.tiles[2].tile_value == 11 ) and \
       ( loc_set.tiles[3].is_teen_or_day() or loc_set.tiles[3].tile_value == 11 ):
      switch_it = True
    
    # we split sevens if the other two are
    # both within (teen, day)
    if pair_tile.tile_value == 7 and \
       ( loc_set.tiles[2].is_teen_or_day() ) and \
       ( loc_set.tiles[3].is_teen_or_day() ):
      switch_it = True
    
    # if the ordering was 1, then the first two or the last
    # two are the pair, and we can just switch the middle
    # two tiles (ordering <-- 2).  If the ordering was 2 or three,
    # then the pair wasn't already there, so we use the
    # tiles in their original order (ordering <-- 1).  We can
    # tell by the ordering: if it's 1, then the first two and
    # last two are pairs.
    if switch_it:
      if ordering == 1:
        ordering = 2
      else:
        ordering = 1
  
  return ordering
  
# return 1 or 2 if one of the sets has one of [ pair, high_nine, gong, wong ]
# and the other doesn't (or has a later-occuring one).  This assumes that
# we have already tested and there isn't an only-way.
def which_has_special_hands( set1, set2 ):
  if PGStrategyLogging.logging:
    print "testing for pairs..."
  ordering = which_set_has_it( set1, set2, PGSet.has_pair )
  if ordering:
    if PGStrategyLogging.logging:
      print "one pair has it: set" + str(ordering)
    return ordering
  
  if PGStrategyLogging.logging:
    print "testing for wong..."
  ordering = which_set_has_it( set1, set2, PGSet.has_wong )
  if ordering:
    if PGStrategyLogging.logging:
      print "one pair has it: set" + str(ordering)
    return ordering

  if PGStrategyLogging.logging:
    print "testing for gong..."
  ordering = which_set_has_it( set1, set2, PGSet.has_gong )
  if ordering:
    if PGStrategyLogging.logging:
      print "one pair has it: set" + str(ordering)
    return ordering

  if PGStrategyLogging.logging:
    print "testing for high nine..."
  ordering = which_set_has_it( set1, set2, PGSet.has_high_nine )
  if ordering:
    if PGStrategyLogging.logging:
      print "one pair has it: set" + str(ordering)
    return ordering
  
  return None
  

# we have two sets that are not only way. choose between them.
def first_set_is_better( set1, set2 ):
  from paigow.pghand import PGHand
  
  # check for only way between these two sets
  if PGStrategyLogging.logging:
    print "\nTesting set " + str(set1) + " against "
    print "        set " + str(set2)
    
  if set1 > set2:
    if PGStrategyLogging.logging:
      print " ... set1 is only way"
    return True
  elif set2 > set1:
    if PGStrategyLogging.logging:
      print " ... set2 is only way"
    return False
  
  if PGStrategyLogging.logging:
    print " ... no only way, using heuristics"
  
  ordering = which_has_special_hands( set1, set2 )
  if ordering:
    if PGStrategyLogging.logging:
      print "one pair has it: set" + str(ordering)
    return ordering == 1

  sum1, diff1 = set1.sum_and_diff()
  sum2, diff2 = set2.sum_and_diff()
  if PGStrategyLogging.logging:
    print " ...sum and diff1: " + str(sum1) + "  " + str(diff1)
    print " ...sum and diff2: " + str(sum2) + "  " + str(diff2)  
  
  # no only way: check for diffs
  #return set1.is_more_even_than( set2 )
  # no only way: check for sums
  return set1.has_higher_sum_than( set2 )

def auto_set_heuristic( set ):
  from paigow.pghand import PGHand
  ordering = ordering_for_special_hands( set )
  if ordering:
    return ordering
  return auto_set_numerical( set )

def auto_set_numerical( set ):
  from paigow.pghand import PGHand
  
  if PGStrategyLogging.logging:
    print "\nauto_set_numerical BEGIN"
  
  picked_ordering = None
  
  # create sets with the three possible combinations.  We'll be re-arranging
  # one of these to create sets so make them editable lists.
  tiles = set.tiles
  if PGStrategyLogging.logging:
    print " ... tiles: [ " + tiles[0].name + ", " + tiles[1].name + ", " + tiles[2].name + ", " + tiles[3].name + " ]"
  tiles1 = [ tiles[0], tiles[1], tiles[2], tiles[3] ]
  tiles2 = [ tiles[0], tiles[2], tiles[1], tiles[3] ]
  tiles3 = [ tiles[0], tiles[3], tiles[1], tiles[2] ]
  sets = ( None, PGSet.create( tiles1 ), PGSet.create( tiles2 ), PGSet.create( tiles3 ) )
  ordering = picked_ordering_for_sets( sets )
  
  # we founds something, re-order the tiles for it.
  if ordering > 0:
    reorder_hands_for_setting( set, ordering )
  else:
    print "WTF? auto_sort didn't find anything?"
  
  return ordering

def picked_ordering_for_sets( sets ):
  if PGStrategyLogging.logging:
    print "\npicked_ordering_for_sets BEGIN..."
    print "set 1: " + str(sets[1])
    print "set 2: " + str(sets[2])
    print "set 3: " + str(sets[3])
  
  picked_ordering = None
  
  # convenience vars to test various combinations
  if True:
    s1beats2 = first_set_is_better( sets[1], sets[2] )
    s2beats1 = first_set_is_better( sets[2], sets[1] )
    s1beats3 = first_set_is_better( sets[1], sets[3] )
    s3beats1 = first_set_is_better( sets[3], sets[1] )
    s2beats3 = first_set_is_better( sets[2], sets[3] )
    s3beats2 = first_set_is_better( sets[3], sets[2] )
  else:
    s1beats2 = sets[1] > sets[2]
    s2beats1 = sets[2] > sets[1]
    s1beats3 = sets[1] > sets[3]
    s3beats1 = sets[3] > sets[1]
    s2beats3 = sets[2] > sets[3]
    s3beats2 = sets[3] > sets[2]
  
  # see if there is an only-way in there
  if s1beats2 and s1beats3:
    picked_ordering = 1
  elif s2beats1 and s2beats3:
    picked_ordering = 2
  elif s3beats1 and s3beats2:
    picked_ordering = 3
  else:
    
    # nope, no only way.  See if there is any set we can remove
    # so we can just compare the other two
    ignore1 = s2beats1 or s3beats1
    ignore2 = s1beats2 or s3beats2
    ignore3 = s2beats3 or s1beats3
    
    if PGStrategyLogging.logging:
      print "    ignore1: " + str(ignore1)
      print "    ignore2: " + str(ignore2)
      print "    ignore3: " + str(ignore3)
    
    if ignore1:
      if first_set_is_better( sets[2], sets[3] ):
        picked_ordering = 2
      else:
        picked_ordering = 3
    elif ignore2:
      if first_set_is_better( sets[1], sets[3] ):
        picked_ordering = 1
      else:
        picked_ordering = 3
    elif ignore3:
      if first_set_is_better( sets[1], sets[2] ):
        picked_ordering = 1
      else:
        picked_ordering = 2
    else:
      # bleah, need 3-way comparison, no only ways between.
      # use the "has" to find the one or ones with pairs etc.
      
      # choose the one with the smallest difference.
      sum1, diff1 = sets[1].sum_and_diff()
      sum2, diff2 = sets[2].sum_and_diff()
      sum3, diff3 = sets[3].sum_and_diff()
      if diff1 < diff2 and diff1 < diff3:
        picked_ordering = 1
      elif diff2 < diff1 and diff2 < diff3:
        picked_ordering = 2
      elif diff3 < diff1 and diff3 < diff2:
        picked_ordering = 3
      else:
        if PGStrategyLogging.logging:
          print " no diff winner, will ordering one or two."
        
        # double-bleah: there was evidently a diff tie.
        # We can't then go to the largest sum because two with a diff
        # tie, where one sum is larger, would be an only way.  So therefore
        # the two with the smallest diff must be the same.  Therefore,
        # since there are two of them, either 1 or 2 has to be it: just
        # compare those.
        if first_set_is_better( sets[1], sets[2] ):
          picked_ordering = 1
        else:
          picked_ordering = 2
  
  if PGStrategyLogging.logging:
    print "picked_ordering_for_sets END returns " + str(picked_ordering) + "\n"
  return picked_ordering

class PGStrategy:
  
  class Meta:
    app_label = 'paigow'
  
  @classmethod
  def auto_set( cls, sets ):
    for set in sets:
      if s_use_numerical_auto_set:
        auto_set_numerical( set )
      else:
        auto_set_heuristic( set )
    
    # order the sets
    ordering_sets = [ None ]
    ordering_sets.extend( sets )
    ordering = picked_ordering_for_sets( ordering_sets )
    if ordering == 1:
      # first set is the best, find the next-best
      if first_set_is_better( sets[1], sets[2] ):
        sets = sets
      else:
        sets = [ sets[0], sets[2], sets[1] ]
    elif ordering == 2:
      # second set is the best, find the next-best
      if first_set_is_better( sets[0], sets[2] ):
        sets = [ sets[1], sets[0], sets[2] ]
      else:
        sets = [ sets[1], sets[2], sets[0] ]
    else:
      # third set is the best, find the next-best
      if first_set_is_better( sets[0], sets[1] ):
        sets = [ sets[2], sets[0], sets[1] ]
      else:
        sets = [ sets[2], sets[1], sets[0] ]
    return sets

# ----------------------------------------------------
# Test PGStrategy class

from django.test import TestCase

class PGStrategyTest( TestCase ):
  
  # we need the set of tiles in the test database
  fixtures = [ 'pgtile.json' ]
  
  def test_auto_set( self ):
    #PGStrategyLogging.logging = True
    set = PGSet.create_with_tile_names( ( "day", "low ten", "mixed five", "eleven" ) )
    self.assertEqual( auto_set_numerical( set ), 2 )
    set = PGSet.create_with_tile_names( ( "low four", "low ten", "eleven", "low six" ) )
    self.assertEqual( auto_set_numerical( set ), 2 )
    set = PGSet.create_with_tile_names( ( "teen", "low six", "harmony four", "long six" ) )
    self.assertEqual( auto_set_numerical( set ), 1 )
    set = PGSet.create_with_tile_names( ( "low four", "mixed nine", "high eight", "mixed eight" ) )
    self.assertEqual( auto_set_numerical( set ), 1 )
    set = PGSet.create_with_tile_names( ( "teen", "low ten", "eleven", "mixed nine" ) )
    self.assertEqual( auto_set_numerical( set ), 3 )
    set = PGSet.create_with_tile_names( ( "low ten", "mixed nine", "day", "high ten" ) )
    self.assertEqual( auto_set_numerical( set ), 3 )
  
  def test_x321_set_ordering( self ):
    set1 = PGSet.create_with_tile_names( ( "low ten", "mixed nine", "harmony four", "low four" ) )
    set2 = PGSet.create_with_tile_names( ( "low six", "low six", "low ten", "high seven" ) )
    self.assertFalse( first_set_is_better( set1, set2 ) )
    
    set1 = PGSet.create_with_tile_names( ( "eleven", "mixed five", "high eight", "high seven" ) )
    set2 = PGSet.create_with_tile_names( ( "low ten", "mixed nine", "high ten", "mixed five" ) )
    self.assertFalse( first_set_is_better( set1, set2 ) )
    
  def special_ordering_for_teen_pair( self, teen_or_day ):
    # test reordering to get pair
    set = PGSet.create_with_tile_names( ( teen_or_day, "eleven", "high eight", teen_or_day ) )
    self.assertEqual( ordering_for_special_hands( set ), 1 )
    
    # test no reordering to get pair
    set = PGSet.create_with_tile_names( ( "eleven", teen_or_day, "high eight", teen_or_day ) )
    self.assertEqual( ordering_for_special_hands( set ), 1 )
    
    # test no reorder to split pair
    set = PGSet.create_with_tile_names( ( "mixed nine", teen_or_day, "high eight", teen_or_day ) )
    self.assertEqual( ordering_for_special_hands( set ), 1 )
    
    # test reorder to split pair
    set = PGSet.create_with_tile_names( ( "mixed nine", "high eight", teen_or_day, teen_or_day ) )
    self.assertEqual( ordering_for_special_hands( set ), 2 )
    
  def test_special_ordering_for_teen_or_day_pairs( self ):
    self.special_ordering_for_teen_pair( "teen" )
    self.special_ordering_for_teen_pair( "day" )
  
  def test_special_ordering_for_high_numbers( self ):
    # test reorder sevens to split pair
    set = PGSet.create_with_tile_names( ( "mixed seven", "mixed seven", "teen", "day" ) )
    self.assertEqual( ordering_for_special_hands( set ), 2 )
    
    # test no reorder sevens to split pair
    set = PGSet.create_with_tile_names( ( "mixed seven", "teen", "mixed seven", "day" ) )
    self.assertEqual( ordering_for_special_hands( set ), 1 )
    
    # test reorder eights to make pair
    set = PGSet.create_with_tile_names( ( "mixed eight", "low ten", "mixed eight", "day" ) )
    self.assertEqual( ordering_for_special_hands( set ), 2 )
    
    # test no reorder eights to make pair
    set = PGSet.create_with_tile_names( ( "low ten", "day", "mixed eight", "mixed eight" ) )
    self.assertEqual( ordering_for_special_hands( set ), 1 )

    # test reorder nines to make pair
    set = PGSet.create_with_tile_names( ( "low ten", "day", "mixed nine", "mixed nine" ) )
    self.assertEqual( ordering_for_special_hands( set ), 2 )


# run the test when invoked as a test (this is boilerplate
# code at the bottom of every python file that has unit
# tests in it).
if __name__ == '__main__':
  unittest.main()

