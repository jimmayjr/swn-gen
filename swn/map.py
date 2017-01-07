#!/usr/bin/env python

# Constants --------------------------------------------------------------------
_IMAGE_BACKGROUND_BRIGHTNESS = 0.8

# Defaults ---------------------------------------------------------------------
# Size
_IMAGE_WIDTH  = 1500 # px
_IMAGE_HEIGHT = 2000 # px
# Margins
_TOP_MARGIN_RATIO    = 0.04
_BOTTOM_MARGIN_RATIO = 0.04
_LEFT_MARGIN_RATIO   = 0.03
_RIGHT_MARGIN_RATIO  = 0.03

# Calculated values ------------------------------------------------------------
_imageSize


## Map class.
#
#  The map class is used to create map images of a SWN sector.
class Map(object):
    ## Map class constructor.
    #  @param self The object pointer.
    def __init__(self):

    ## Set map parameters.
    #  @param self The object pointer.
    def SetParams(self,
                  width             = _IMAGE_WIDTH,
                  height            = _IMAGE_HEIGHT,
                  topMarginRatio    = _TOP_MARGIN_RATIO,
                  bottomMarginRatio = _BOTTOM_MARGIN_RATIO,
                  leftMarginRatio   = _LEFT_MARGIN_RATIO,
                  rightMarginRatio  = _RIGHT_MARGIN_RATIO):

## Documentation for a method.
#  @param self The object pointer.