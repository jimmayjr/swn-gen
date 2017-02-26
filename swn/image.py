#!/usr/bin/env python

import math
import numpy as np
import os
import PIL.Image as pilimage
import PIL.ImageDraw as pildraw
import PIL.ImageEnhance as pilenhance
import PIL.ImageFilter as pilfilter
import PIL.ImageFont as pilfont
import scipy.interpolate as spi

_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Colors -----------------------------------------------------------------------
_COLORS = dict()
_COLORS['black']        = (0,0,0,255)
_COLORS['blue']         = (0,0,255,255)
_COLORS['cyan']         = (0,255,255,255)
_COLORS['green']        = (0,255,0,255)
_COLORS['magenta']      = (255,0,255,255)
_COLORS['orange']       = (255,100,0,255)
_COLORS['red']          = (255,0,0,255)
_COLORS['yellow']       = (255,255,0,255)
_COLORS['white']        = (255,255,255,255)
_COLORS['grey']         = (150,150,150,255)
# Light Colors
_COLORS['lightgrey']    = (200,200,200,255)
# Dark Colors
_COLORS['darkblue']     = (0,0,100,255)
_COLORS['darkgreen']    = (0,150,0,255)
_COLORS['darkgrey']     = (50,50,50,255)
_COLORS['darkred']      = (100,0,0,255)
_COLORS['darkyellow']   = (100,100,0,255)
# Theme colors
_COLORS['themeblue']    = (119,158,203,255)
_COLORS['themegreen']   = (119,190,119,255)
_COLORS['thememagenta'] = (244,154,194,255)
_COLORS['themeorange']  = (216,149,32,255)
_COLORS['themepurple']  = (170,65,202,255)
_COLORS['themered']     = (194,59,34,255)
_COLORS['themeyellow']  = (253,253,150,255)
_COLORS['themedarkred'] = (150,0,0,255)

# Sector Defaults --------------------------------------------------------------
# Size
_SECTOR_IMAGE_WIDTH  = 1500 # px
_SECTOR_IMAGE_HEIGHT = 2000 # px

# Margins
_SECTOR_TOP_MARGIN_RATIO    = 0.04
_SECTOR_BOTTOM_MARGIN_RATIO = 0.04
_SECTOR_LEFT_MARGIN_RATIO   = 0.03
_SECTOR_RIGHT_MARGIN_RATIO  = 0.03

# Drawing specifications -------------------------------------------------------
_IMAGE_BACKGROUND            = os.path.join(_DIR_PATH,'images/starfield.png')
_IMAGE_BACKGROUND_BRIGHTNESS = 0.8
_ROUTE_WIDTH_RATIO           = 1./10.
_ROUTE_BLUR_SIZE_RATIO       = 0.6
_ROUTE_COLOR                 = (179,235,250,100)
_GRID_WIDTH_RATIO            = 3./1500.
_GRID_COLOR                  = (100,100,100,255)
_GRID_ALPHA                  = 200
_STAR_LARGE_DIAMETER_RATIO   = 1./4.
_STAR_MEDIUM_DIAMETER_RATIO  = 1./5.
_STAR_SMALL_DIAMETER_RATIO   = 1./6.
_STAR_DIAMETER_RATIO         = _STAR_MEDIUM_DIAMETER_RATIO
_STAR_OUTLINE_COLOR          = _COLORS['black']
_STAR_COLOR                  = _COLORS['lightgrey']
_ANGLE_BETWEEN_WORLDS        = 60
_WORLD_ORBIT_RADIUS_RATIO    = 1./5.
_WORLD_LARGE_DIAMETER_RATIO  = 1./7.
_WORLD_MEDIUM_DIAMETER_RATIO = 1./9.
_WORLD_SMALL_DIAMETER_RATIO  = 1./11.
_WORLD_DIAMETER_RATIO        = _WORLD_MEDIUM_DIAMETER_RATIO
_WORLD_COLOR                 = _COLORS['lightgrey']
_TRIANGLE_LENGTH_RATIO       = 1./6.
_TRIANGLE_MARGIN_RATIO       = 1./40.
_FACTION_ALPHA               = 35

# Font specifications
_FONT_FILENAME               = os.path.join(_DIR_PATH,'fonts/mplus-1m-regular.ttf')
_HEX_FONT_SIZE_RATIO         = 1./6.
_HEX_FONT_COLOR              = _COLORS['grey']
_HEX_NUM_MARGIN_RATIO        = 1./18.
_SYSTEM_NAME_FONT_SIZE_RATIO = 1./6.5
_SYSTEM_FONT_COLOR           = _COLORS['lightgrey']
_SYSTEM_NAME_MARGIN_RATIO    = 1./3.
_INFO_FONT_SIZE_RATIO        = 1./6.
_INFO_MARGIN_RATIO           = 1./6.
_SECTOR_FONT_FILENAME        = _FONT_FILENAME
_LIST_FONT_FILENAME          = _FONT_FILENAME


## Sector image class.
#
#  The sector image class is used to create images of an SWN sector.
class SectorImage(object):
    ## Sector image class constructor.
    #  @param self The object pointer.
    #  @param rows              Number of hex rows.
    #  @param cols              Number of hex columns.
    #  @param width             Image width in pixels.
    #  @param height            Image height in pixels.
    #  @param topMarginRatio    Top margin ratio relative to height.
    #  @param bottomMarginRatio Bottom margin ratio relative to height.
    #  @param leftMarginRatio   Left margin ratio relative to width.
    #  @param rightMarginRatio  Right margin ratio relative to width.
    def __init__(self,
                 rows,
                 cols,
                 width             = None,
                 height            = None,
                 topMarginRatio    = None,
                 bottomMarginRatio = None,
                 leftMarginRatio   = None,
                 rightMarginRatio  = None):
        # Check arguments
        self._rows        = exception.arg_check(rows,              int)
        self._cols        = exception.arg_check(cols,              int)
        width             = exception.arg_check(width,             int, _SECTOR_IMAGE_WIDTH)
        height            = exception.arg_check(height,            int, _SECTOR_IMAGE_HEIGHT)
        topMarginRatio    = exception.arg_check(topMarginRatio,    int, _SECTOR_TOP_MARGIN_RATIO)
        bottomMarginRatio = exception.arg_check(bottomMarginRatio, int, _SECTOR_BOTTOM_MARGIN_RATIO)
        leftMarginRatio   = exception.arg_check(leftMarginRatio,   int, _SECTOR_LEFT_MARGIN_RATIO)
        rightMarginRatio  = exception.arg_check(rightMarginRatio,  int, _SECTOR_RIGHT_MARGIN_RATIO)

        # Set sector map parameters
        set_params(width, height, topMarginRatio, bottomMarginRatio, leftMarginRatio, rightMarginRatio)

    ## Set image parameters.
    #  @param self              The object pointer.
    #  @param width             Image width in pixels.
    #  @param height            Image height in pixels.
    #  @param topMarginRatio    Top margin ratio relative to height.
    #  @param bottomMarginRatio Bottom margin ratio relative to height.
    #  @param leftMarginRatio   Left margin ratio relative to width.
    #  @param rightMarginRatio  Right margin ratio relative to width.
    def set_params(self,
                   width             = None,
                   height            = None,
                   topMarginRatio    = None,
                   bottomMarginRatio = None,
                   leftMarginRatio   = None,
                   rightMarginRatio  = None):
        # Check arguments
        width             = exception.arg_check(width,             int, _SECTOR_IMAGE_WIDTH)
        height            = exception.arg_check(height,            int, _SECTOR_IMAGE_HEIGHT)
        topMarginRatio    = exception.arg_check(topMarginRatio,    int, _SECTOR_TOP_MARGIN_RATIO)
        bottomMarginRatio = exception.arg_check(bottomMarginRatio, int, _SECTOR_BOTTOM_MARGIN_RATIO)
        leftMarginRatio   = exception.arg_check(leftMarginRatio,   int, _SECTOR_LEFT_MARGIN_RATIO)
        rightMarginRatio  = exception.arg_check(rightMarginRatio,  int, _SECTOR_RIGHT_MARGIN_RATIO)

        # Bounding box
        topMargin    = int(height*topMarginRatio)
        bottomMargin = int(height*bottomMarginRatio)
        leftMargin   = int(width*leftMarginRatio)
        rightMargin  = int(width*rightMarginRatio)
        marginHeight = height - topMargin - bottomMargin
        marginWidth  = width - leftMargin - rightMargin
        topLeft      = (leftMargin,        topMargin)
        topRight     = (width-rightMargin, topMargin)
        bottomRight  = (width-rightMargin, height-bottomMargin)
        bottomLeft   = (leftMargin,        height-bottomMargin)

        # Hex sizes
        hexSizeByHeight = float((float(2)/math.sqrt(3))*(float(marginHeight)/float(2*rows+1)))
        hexSizeByWidth  = float(2.0*marginWidth)/float(3.0*cols+1.0)
        hexSize         = min(hexSizeByHeight,hexSizeByWidth)
        hexWidth        = float(hexSize*2.0)
        hexHeight       = float(float(math.sqrt(3.0)/2.0)*float(hexWidth))

        # Map Bounding Box
        if (hexSize == hexSizeByWidth):
            mapWidth       = marginWidth
            mapHeight      = (math.sqrt(3.0)/2.0)*hexSize*(2.0*rows+1)
            offsetY        = (marginHeight-self.mapHeight)/2.0
            mapTopLeft     = (topLeft[0],     topLeft[1]+offsetY)
            mapTopRight    = (topRight[0],    topRight[1]+offsetY)
            mapBottomRight = (bottomRight[0], bottomRight[1]-offsetY)
            mapBottomLeft  = (bottomLeft[0],  bottomLeft[1]-offsetY)
        else:
            mapWidth       = hexSize*(1.0/2.0)*(3.0*cols+1)
            mapHeight      = marginHeight
            offsetX        = (marginWidth-self.mapWidth)/2.0
            mapTopLeft     = (topLeft[0]+offsetX,     topLeft[1])
            mapTopRight    = (topRight[0]-offsetX,    topRight[1])
            mapBottomRight = (bottomRight[0]-offsetX, bottomRight[1])
            mapBottomLeft  = (bottomLeft[0]+offsetX,  bottomLeft[1])

        # Drawing specifications
        routeWidth       = int(hexSize*_ROUTE_WIDTH_RATIO)
        routeBlurSize    = routeWidth*_ROUTE_BLUR_SIZE_RATIO
        gridWidth        = int(routeWidth*_GRID_WIDTH_RATIO)
        starDiameter     = int(hexSize*_STAR_DIAMETER_RATIO)
        worldOrbitRadius = int(hexHeight*_WORLD_ORBIT_RADIUS_RATIO)
        worldDiameter    = int(hexSize*_World_DIAMETER_RATIO)
        triangleLength   = int(hexSize*_TRIANGLE_LENGTH_RATIO)
        triangleMargin   = int(hexHeight*_TRIANGLE_MARGIN_RATIO)

        # Font specifications
        hexFontSize        = int(hexHeight*_HEX_FONT_SIZE_RATIO)
        hexFont            = pilfont.truetype(_FONT_FILENAME, hexFontSize, encoding="unic")
        hexNumMargin       = int(hexHeight*_HEX_NUM_MARGIN_RATIO)
        systemNameFontSize = int(hexHeight*_SYSTEM_NAME_FONT_SIZE_RATIO)
        systemNameFont     = pilfont.truetype(_FONT_FILENAME, systemNameFontSize, encoding="unic")
        infoFontSize       = int(hexHeight*_INFO_FONT_SIZE_RATIO)
        infoFont           = pilfont.truetype(_FONT_FILENAME, infoFontSize, encoding="unic")
        infoMargin         = int(hexSize*_INFO_MARGIN_RATIO)

        # Store values
        self._size             = (width, height)
        self._mapTopLeft       = mapTopLeft
        self._mapTopRight      = mapTopRight
        self._mapBottomRight   = mapBottomRight
        self._mapBottomLeft    = mapBottomLeft
        self._hexSize          = hexSize
        self._routeWidth       = routeWidth
        self._routeBlurSize    = routeBlurSize
        self._gridWidth        = gridWidth
        self._starDiameter     = starDiameter
        self._worldOrbitRadius = worldOrbitRadius
        self._worldDiameter    = worldDiameter
        self._triangleLength   = triangleLength
        self._triangleMargin   = triangleMargin
        self._hexFont          = hexFont
        self._hexNumMargin     = hexNumMargin
        self._systemNameFont   = systemNameFont
        self._infoFont         = infoFont
        self._infoMargin       = infoMargin