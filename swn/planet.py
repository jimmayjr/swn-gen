#!/usr/bin/env python

import abc

# Tables -----------------------------------------------------------------------
#One Roll Star System
TABLE_PLANET_TYPE = {
    'COLD_STONE': 'cold stone',
    'HOT_ROCK':   'hot rock',
    'ICE':        'ice',
    'INHABITED':  'inhabited',
    'LARGE_GAS':  'large gas',
    'SMALL_GAS':  'small gas'
}

# Base Planet class ------------------------------------------------------------
class BasePlanet(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def __init__(self,
                 planetType=TABLE_PLANET_TYPE['INHABITED']):
        self.planetType = planetType