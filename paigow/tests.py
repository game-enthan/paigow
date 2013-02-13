# this is where the django test command looks.  By importing into
# here we advertise our test cases.  The ones in 'models' are
# already handled in __init__.py in that directory.

from pghand import PGHandTest
from pgset import PGSetTest
from pgstrategy import PGStrategyTest
from pgdot import PGDotTest
