#!/usr/bin/env python

import abc

import exception
import world

# Tables -----------------------------------------------------------------------
# One Roll Star System
# Moon size
TABLE_MOON_SIZE = {
    'SMALL':  'small',
    'MEDIUM': 'medium'
}

TABLE_MEDIUM_MOONS = {
    1:  0,
    2:  1,
    3:  0,
    4:  0,
    5:  0,
    6:  0,
    7:  0,
    8:  0,
    9:  0,
    10: 0,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
    15: 0,
    16: 0,
    17: 2,
    18: 0,
    19: 0,
    20: 1
}

TABLE_MINOR_RINGS = {
    1:  True,
    2:  False,
    3:  True,
    4:  False,
    5:  False,
    6:  False,
    7:  False,
    8:  False,
    9:  False,
    10: False,
    11: False,
    12: False,
    13: False,
    14: False,
    15: False,
    16: False,
    17: False,
    18: False,
    19: False,
    20: False
}

TABLE_SMALL_MOONS = {
    1:  0,
    2:  0,
    3:  0,
    4:  0,
    5:  0,
    6:  0,
    7:  0,
    8:  0,
    9:  0,
    10: 0,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
    15: 1,
    16: 1,
    17: 2,
    18: 2,
    19: 3,
    20: 3
}

# Orbital object type
TABLE_ORBITAL_OBJECT_TYPE = {
    'COLD_STONE':                'cold stone',
    'HOT_ROCK':                  'hot rock',
    'HYDROCARBON_ASTEROID_BELT': 'hydrocarbon astroid belt',
    'ICE':                       'ice',
    'ICY_ASTEROID_BELT':         'icy asteroid belt',
    'ROCKY':                     'rocky',
    'LARGE_GAS':                 'large gas',
    'MEDIUM_MOON':               'medium moon',
    'METALLIC_ASTEROID_BELT':    'metal asteroid belt',
    'ROCKY_ASTEROID_BELT':       'rocky asteroid belt',
    'SMALL_GAS':                 'small gas',
    'SMALL_MOON':                'small moon',
    'SPACE_STATION':             'space station'
}

# Base orbital object class ----------------------------------------------------
class BaseOrbitalObject(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def __init__(self,
                 objectType = None,
                 worldObj   = None):
        # Check arguments
        self.objectType = exception.arg_check(objectType,str)
        self.world      = exception.arg_check(worldObj,world.World,None)

    def world_list(self):
        if ( self.world == None ):
            return([])
        else:
            return([self.world])

# Asteroid belt class ----------------------------------------------------------
class AsteroidBelt(BaseOrbitalObject):
    def __init__(self,
                 objectType = None):
        # Initialize base class
        BaseOrbitalObject.__init__(self,
                                   objectType = exception.arg_check(objectType,str,TABLE_ORBITAL_OBJECT_TYPE['ROCKY_ASTEROID_BELT']))

# Moon class -------------------------------------------------------------------
class Moon(BaseOrbitalObject):
    def __init__(self,
                 objectType = None,
                 worldObj   = None):
        # Initialize base class
        BaseOrbitalObject.__init__(self,
                                   objectType = exception.arg_check(objectType,str,TABLE_ORBITAL_OBJECT_TYPE['SMALL_MOON']),
                                   worldObj   = exception.arg_check(worldObj,world.World,None))

# Planet class -----------------------------------------------------------------
class Planet(BaseOrbitalObject):
    def __init__(self,
                 objectType = None,
                 stations   = None,
                 moons      = None,
                 rings      = None,
                 worldObj   = None):
        # Check arguments
        self.stations = exception.arg_check(stations, list,        list())
        self.moons    = exception.arg_check(moons,    list,        list())
        self.rings    = exception.arg_check(rings,    bool,        False)
        # Initialize base class
        BaseOrbitalObject.__init__(self,
                                   objectType = exception.arg_check(objectType,str,TABLE_ORBITAL_OBJECT_TYPE['ROCKY']),
                                   worldObj   = exception.arg_check(worldObj,world.World,None))

    def world_list(self):
        worlds  = BaseOrbitalObject.world_list(self)
        for s in self.stations:
            worlds += s.world_list()
        for m in self.moons:
            worlds += m.world_list()
        return(worlds)

# Space station class ----------------------------------------------------------
class SpaceStation(BaseOrbitalObject):
    def __init__(self,
                 worldObj = None):
        # Initialize base class
        BaseOrbitalObject.__init__(self,
                                   objectType = TABLE_ORBITAL_OBJECT_TYPE['SPACE_STATION'],
                                   worldObj   = exception.arg_check(worldObj,world.World,None))