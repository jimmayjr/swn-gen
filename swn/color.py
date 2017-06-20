#!/usr/bin/env python

import exception

# Class ------------------------------------------------------------------------
## RGB(A) color class.
#
# Contains [0,255] integer values for red, green, and blue.
class Color(object):
    def __init__(self, r, g, b, a=None):
        # Set color will check arguments for creating a color
        self.set_rgba(r, g, b, a)

    ## Return rgb of color
    def rgb(self):
        return (self._r, self._g, self._b)

    ## Return rgba of color or rgb with temporary new alpha value.
    def rgba(self, a=None):
        # Check argument types
        a = exception.arg_check(a, int, self._a)
        # Check argument ranges
        a = exception.arg_range_check(a, 0, 255)
        # Return rgba
        return (self._r, self._g, self._b, a)

    # Set color by 
    def set_color(self, _color):
        # Check arguments
        _color = exception.arg_check(_color, Color, NONE)
        # Set rgba values from _color argument
        r,g,b,a = _color.rgba()
        self.set_rgba(r,g,b,a)

    def set_rgb(self, r, g, b):
        # set_rgba will check arguments
        self.set_rgba(r,g,b)

    def set_rgba(self, r, g, b, a=None):
        # Check arguments
        r = exception.arg_check(r, int)
        g = exception.arg_check(g, int)
        b = exception.arg_check(b, int)
        a = exception.arg_check(a, int, 255)

        # Check r,g,b,a ranges
        self._r = exception.arg_range_check(r, 0, 255)
        self._g = exception.arg_range_check(g, 0, 255)
        self._b = exception.arg_range_check(b, 0, 255)
        self._a = exception.arg_range_check(a, 0, 255)


# Default colors ---------------------------------------------------------------
# Empty color
NONE           = Color(0,0,0,0)
# Standard colors
BLACK          = Color(0,0,0)
BLUE           = Color(0,0,255)
CYAN           = Color(0,255,255)
GREEN          = Color(0,255,0)
MAGENTA        = Color(255,0,255)
ORANGE         = Color(255,100,0)
RED            = Color(255,0,0)
YELLOW         = Color(255,255,0)
WHITE          = Color(255,255,255)
GREY           = Color(150,150,150)
# Light colors
LIGHT_GREY     = Color(200,200,200)
# Dark colors
DARK_BLUE      = Color(0,0,100)
DARK_GREEN     = Color(0,150,0)
DARK_GREY      = Color(50,50,50)
DARK_RED       = Color(100,0,0)
DARK_YELLOW    = Color(100,100,0)
# Theme colors
THEME_BLUE     = Color(119,158,203)
THEME_GREEN    = Color(119,190,119)
THEME_GREY     = Color(100,100,100)
THEME_MAGENTA  = Color(244,154,194)
THEME_ORANGE   = Color(216,149,32)
THEME_PURPLE   = Color(170,65,202)
THEME_RED      = Color(194,59,34)
THEME_YELLOW   = Color(253,253,150)
THEME_DARK_RED = Color(150,0,0)