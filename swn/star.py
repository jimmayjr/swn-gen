#!/usr/bin/env python

import color
import exception
import numpy as np

# Tables -----------------------------------------------------------------------
# One Roll Star System tables
# Star color text.
TABLE_COLOR = {
    1: 'red',
    2: 'white',
    3: 'light yellow',
    4: 'yellow',
    5: 'orange'
}

# Star sequence based on color.
TABLE_COLOR_SEQUENCE = {
    1: 'M',
    2: 'A',
    3: 'F',
    4: 'G',
    5: 'K'
}

# Star color id and text
TABLE_COLOR_ID      = {}
TABLE_COLOR_TEXT    = {}
TABLE_COLOR_ID[0]   = 1
TABLE_COLOR_TEXT[0] = 'red dwarf (M), size V'
TABLE_COLOR_ID[1]   = 2
TABLE_COLOR_TEXT[1] = 'white (A), size V'
for i in xrange(2,10):
    TABLE_COLOR_ID[i]   = 3
    TABLE_COLOR_TEXT[i] = 'light yellow (F), size V'
for i in xrange(10,12):
    TABLE_COLOR_ID[i]   = 4
    TABLE_COLOR_TEXT[i] = 'yellow (G), size V'
TABLE_COLOR_ID[12]   = 5
TABLE_COLOR_TEXT[12] = 'orange (K), size V'
for i in xrange(13,31):
    TABLE_COLOR_ID[i]   = 1
    TABLE_COLOR_TEXT[i] = 'red dwarf (M), size V'

_TABLE_COLOR_ID_ORDER = [1,2,10,12,13]

# Star spectral class d12 roll modifier
TABLE_SPECTRAL_MODIFIER = {
    1: 0,
    2: 12,
    3: 12,
    4: 0,
    5: 0,
    6: 0
}

# Star spectral subclass d10 roll
TABLE_SPECTRAL_SUBCLASS = {}
for i in xrange(1,11):
    TABLE_SPECTRAL_SUBCLASS[i] = i-1

# Other tables
TABLE_MASS_MAP = {
    'A': (1.4,  2.1),
    'F': (1.04, 1.4),
    'G': (0.8,  1.04),
    'K': (0.45, 0.8),
    'M': (0.08, 0.45)
}

TABLE_RADIUS_MAP = {
    'A': (1.4,  1.8),
    'F': (1.15, 1.4),
    'G': (0.96, 1.15),
    'K': (0.7,  0.96),
    'M': (0.2,  0.7)
}

# Star class -------------------------------------------------------------------
class Star(object):
    def __init__(self,
                 color               = None,
                 colorText           = None,
                 classification      = None,
                 spectralSubclass    = None,
                 spectralSubclassMod = None,
                 luminosity          = None):
        # Check arguments.
        self.color               = exception.arg_check(color,            str, '')
        self.colorText           = exception.arg_check(colorText,        str, '')
        self.classification      = exception.arg_check(classification,   str, '')
        self.spectralSubclass    = exception.arg_check(spectralSubclass, int, 0)
        self.luminosity          = exception.arg_check(luminosity,       str, 'V')
        exception.arg_check(spectralSubclassMod, float, 0)
        
        # Calculate other star data equation.
        # y is value from table
        # x is modified subclass in range [0,1]
        # y = Ax + B
        # y = ((y1-y0)/(x1-x0))*x + B
        MASS_A = TABLE_MASS_MAP[classification][1]-TABLE_MASS_MAP[classification][0]
        MASS_B = TABLE_MASS_MAP[classification][0] # Because x0 is 0
        RADIUS_A = TABLE_RADIUS_MAP[classification][1]-TABLE_RADIUS_MAP[classification][0]
        RADIUS_B = TABLE_RADIUS_MAP[classification][0] # Because x0 is 0
        # Calculate values.
        self.solarMass   = MASS_A*spectralSubclassMod + MASS_B
        self.solarRadius = RADIUS_A*spectralSubclassMod + RADIUS_B