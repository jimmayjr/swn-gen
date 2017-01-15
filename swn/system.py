#!/usr/bin/env python

import exception
import orbitalobject
import star

# Tables -----------------------------------------------------------------------
# SWN tables
# Inhabited worlds per system
TABLE_WORLDS = {
    1:  1,
    2:  1,
    3:  1,
    4:  1,
    5:  1,
    6:  1,
    7:  2,
    8:  2,
    9:  2,
    10: 3 
}

# One Roll Star System tables
# Number of hydrocarbon asteroid belts per system
TABLE_HYDROCARBON_INNER_ASTEROID_BELTS = {d: 0 for d in xrange(1,9)}

TABLE_HYDROCARBON_OUTER_ASTEROID_BELTS = {
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 1
}

# Number of icy asteroid belts per system
TABLE_ICY_INNER_ASTEROID_BELTS = {d: 0 for d in xrange(1,9)}

TABLE_ICY_OUTER_ASTEROID_BELTS = {
    1: 1,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 1,
    8: 0
}

# Number of metallic asteroid belts per system
TABLE_METALLIC_INNER_ASTEROID_BELTS = {
    1: 0,
    2: 1,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 1
}

TABLE_METALLIC_OUTER_ASTEROID_BELTS = {d: 0 for d in xrange(1,9)}

# Number of rocky asteroid belts per system
TABLE_ROCKY_INNER_ASTEROID_BELTS = {
    1: 1,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 0
}

TABLE_ROCKY_OUTER_ASTEROID_BELTS = {
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 1,
    7: 0,
    8: 0
}


# Number of large gas giants per system
TABLE_GAS_GIANT_LARGE = {
    1:  1,
    2:  1,
    3:  1,
    4:  0,
    5:  0,
    6:  0,
    7:  1,
    8:  0,
    9:  2,
    10: 2
}

# Number of small gas giants per system
TABLE_GAS_GIANT_SMALL = {
    1:  2,
    2:  1,
    3:  0,
    4:  1,
    5:  0,
    6:  1,
    7:  0,
    8:  2,
    9:  0,
    10: 1
}

# Main world orbit
TABLE_MAIN_WORLD_ORBIT = {
    1: 1,
    2: 1,
    3: 1,
    4: 0,
    5: 0,
    6: 0
}

# Main world orbit modifier
TABLE_MAIN_WORLD_ORBIT_MOD = {
    0:  0,
    1:  5,
    2:  4,
    3:  4,
    4:  4,
    5:  4,
    6:  3,
    7:  3,
    8:  3,
    9:  3,
    10: 3,
    11: 2,
    12: 2,
    13: 1,
    14: 1,
    15: 1,
    16: 1,
    17: 1,
    18: 1,
    19: 1,
    20: 1,
    21: 1,
    22: 1,
    23: 1,
    24: 1,
    25: 1,
    26: 1,
    27: 1,
    28: 1,
    29: 1,
    30: 1
}

# Number of stars per system
TABLE_STARS = {
    1: 1,
    2: 1,
    3: 1,
    4: 2,
    5: 2
}

# Star system class ------------------------------------------------------------
class System(object):
    def __init__(self,
                 name    = None,
                 stars   = None,
                 objects = None,
                 worlds  = None):
        # Check arguments
        self.name    = exception.arg_check(name,str,'')
        self.stars   = exception.arg_check(stars,list,list())
        self.objects = exception.arg_check(objects,list,list())
        for o in objects:
            if not (isinstance(o,orbitalobject.BaseObject)):
                raise exception.InvalidListItemType(o,orbitalobject.BaseObject)
        self.worlds  = exception.arg_check(worlds,list,list())

    def sorted_worlds(self):
        return(sorted(self.worlds, key=lambda w: w.name))