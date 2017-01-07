#!/usr/bin/env python

import exception

# Tables -----------------------------------------------------------------------
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

# Star class -------------------------------------------------------------------
class Star(object):
    def __init__(self):
        pass

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