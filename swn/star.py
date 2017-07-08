#!/usr/bin/env python

import color
import exception

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



# Star class -------------------------------------------------------------------
class Star(object):
    def __init__(self,
                 color            = None,
                 colorText        = None,
                 classification   = None,
                 spectralSubclass = None):
        # Check arguments
        exception.arg_check(color,str,'')
        exception.arg_check(colorText,str,'')
        exception.arg_check(classification,str,'')
        exception.arg_check(spectralSubclass,int,0)

        # Star information
        self.color            = color
        self.colorText        = colorText
        self.classification   = classification
        self.spectralSubclass = spectralSubclass