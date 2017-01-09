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
TABLE_HYDROCARBON_ASTEROID_BELTS = {
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
TABLE_ICY_ASTEROID_BELTS = {
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
TABLE_METALLIC_ASTEROID_BELTS = {
    1: 0,
    2: 1,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 1
}

# Number of rocky asteroid belts per system
TABLE_ROCKY_ASTEROID_BELTS = {
    1: 1,
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
TABLE_MAIN_WORLD_ORBIT = {}
for i in xrange(1,4):
    TABLE_MAIN_WORLD_ORBIT[i] = 1
for i in xrange(4,7):
    TABLE_MAIN_WORLD_ORBIT[i] = 0

# Main world orbit modifier
TABLE_MAIN_WORLD_ORBIT_MOD = {}
TABLE_MAIN_WORLD_ORBIT_MOD[0] = 0
TABLE_MAIN_WORLD_ORBIT_MOD[1] = 5
for i in xrange(2,6):
    TABLE_MAIN_WORLD_ORBIT_MOD[i] = 4
for i in xrange(6,11):
    TABLE_MAIN_WORLD_ORBIT_MOD[i] = 3
for i in xrange(11,13):
    TABLE_MAIN_WORLD_ORBIT_MOD[i] = 2
for i in xrange(13,31):
    TABLE_MAIN_WORLD_ORBIT_MOD[i] = 1

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
                 name = '',
                 stars = list(),
                 objects = list(),
                 worlds = list()):
        # Check arguments
        #   name
        if not (isinstance(name,str)):
            raise exception.InvalidArgType(name,str)
        #   stars
        if not (isinstance(stars,list)):
            raise exception.InvalidArgType(stars,list)
        for s in stars:
            if not (isinstance(s,Star)):
                raise exception.InvalidListItemType(s,star.Star)
        #   orbital objects
        if not (isinstance(objects,list)):
            raise exception.InvalidArgType(objects,list)
        for o in objects:
            if not (isinstance(o,orbitalobject.BaseObject)):
                raise exception.InvalidListItemType(o,orbitalobject.BaseObject)
        
        # General information
        self.name = name

        # SWN rolled information
        self.worlds = worlds

        # System generator rolled information
        self.objects = objects
        self.stars = stars