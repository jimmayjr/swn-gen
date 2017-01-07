#!/usr/bin/env python

import exception

# Tables -----------------------------------------------------------------------
# SWN tables
# Inhabited worlds per system
TABLE_WORLDS_PER_SYSTEM = {
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
TABLE_STARS_PER_SYSTEM = {
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
                 planets = list(),
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
                raise exception.InvalidListItemType(s,Star)
        #   planets
        if not (isinstance(planets,list)):
            raise exception.InvalidArgType(planets,list)
        for p in planets:
            if not (isinstance(p,planet.BasePlanet)):
                raise exception.InvalidListItemType(p,planet.BasePlanet)
        
        # General information
        self.name = name

        # SWN rolled information
        self.worlds = worlds

        # System generator rolled information
        self.planets = planets
        self.stars = stars