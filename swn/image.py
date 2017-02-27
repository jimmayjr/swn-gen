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

import exception
import hexutils

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

# Margins
_SECTOR_TOP_MARGIN_RATIO    = 0.02
_SECTOR_BOTTOM_MARGIN_RATIO = 0.02
_SECTOR_LEFT_MARGIN_RATIO   = 0.04
_SECTOR_RIGHT_MARGIN_RATIO  = 0.04

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

## Hex grid class.
#
#  The hex grid class is used to create a hex grid image to display in the 
#  sector hex grid map.
class HexGrid(object):
    ## Hex grid class constructor.
    #  @param self       The object pointer.
    #  @param rows       Number or rows in the grid.
    #  @param cols       Number of columns in the grid.
    #  @param width      Width of the grid image [px].
    #  @param height     Height of the grid image [px].
    #  @param hexSize    Size of the grid hexes [px].
    #  @param gridWidth  Width of the grid lines [px].
    #  @param leftMargin Left margin of the grid image [px].
    #  @param topMargin  Top margin of the grid image [px].
    def __init__(self,
                 rows,
                 cols,
                 width,
                 height,
                 hexSize,
                 gridWidth,
                 leftMargin = None,
                 topMargin  = None):
        # Check arguments
        self._rows       = exception.arg_check(rows,       int)
        self._cols       = exception.arg_check(cols,       int)
        self._width      = exception.arg_check(width,      int)
        self._height     = exception.arg_check(height,     int)
        self._hexSize    = exception.arg_check(hexSize,    float)
        self._gridWidth  = exception.arg_check(gridWidth,  int)
        self._leftMargin = exception.arg_check(leftMargin, int, math.ceil(gridWidth/2.))
        self._topMargin  = exception.arg_check(topMargin,  int, math.ceil(gridWidth/2.))
        
        # Working image. Leave as None until ready to draw.
        self.workingImage = None

    def draw(self):
        # Blank image before drawing
        if self.workingImage is not None:
            self.workingImage.close()
        self.workingImage = pilimage.new("RGBA", (width,height))
        # List of lines to draw between vertices
        gridLines = list()
        # For each row
        for row in xrange(self._rows):
            # For each column
            for col in xrange(self._cols):
                # Center of hex in integer pixels
                (xc, yc) = hexutils.odd_q_center(self._hexSize, row, col)
                (xc, yc) = (int(xc), int(yc))
                # Offset centers by margins
                (xc, yc) = (xc + self._leftMargin, yc + self._topMargin)
                # Generate pairs of vertices to draw
                for vertex in xrange(0,5):
                    # Get vertex positions in integer pixels
                    (x0, y0) = flat_vertex(self._hexSize, vertex)
                    (x1, y1) = flat_vertex(self._hexSize, vertex+1)
                    # Convert vertices to integer pixels
                    (x0, y0) = (int(x0), int(y0))
                    (x1, y1) = (int(x1), int(y1))
                    # Offset vertices by margins
                    (x0, y0) = (x0 + self._leftMargin, y0 + self._topMargin)
                    (x1, y1) = (x1 + self._leftMargin, y1 + self._topMargin)
                    # Add pair of vertices to list if they aren't already
                    if ((x0+xc, y0+yc), (x1+xc, y1+yc)) not in gridLines:
                        gridLines.append(((x0+xc, y0+yc), (x1+xc, y1+yc)))
        # Create drawing image
        drawingImage = pildraw.Draw(self._workingImage)
        # Draw grid vertex lines
        fillColor = _GRID_COLOR
        lineWidth = int(_GRID_WIDTH_RATIO*self._width)
        for gl in gridLines:
            drawingImage([gl[0], gl[1]], fill=fillColor, width=lineWidth)



## Hex map class.
#
#  The hex maps class is used to create a sector hex map.
class HexMap(object):
    ## Hex sector class constructor.
    #  @param rows    Number of hex rows.
    #  @param cols    Number of hex columns.
    #  @param self    The object pointer.
    #  @param width   The width of the sector image [px].
    #  @param height  The height of the sector image [px].
    #  @param hexSize The hex size to draw the system in [px].
    #  @param gridWidth  Width of the grid lines [px].
    #  @param leftMargin Left margin of the grid image [px].
    #  @param topMargin  Top margin of the grid image [px].
    def __init__(self,
                 rows,
                 cols,
                 width,
                 height,
                 hexSize,
                 gridWidth,
                 leftMargin,
                 topMargin):
        # Check arguments
        exception.arg_check(rows,        int)
        exception.arg_check(cols,        int)
        exception.arg_check(width,       int)
        exception.arg_check(height,      int)
        exception.arg_check(hexSize,     float)
        exception.arg_check(gridWidth,   int)
        self._leftMargin = exception.arg_check(leftMargin, int, math.ceil(gridWidth/2.))
        self._topMargin  = exception.arg_check(topMargin,  int, math.ceil(gridWidth/2.))
        # Create background image

        # Create sector routes

        # Create sector grid
        self.hexGrid = HexGrid(rows, cols, width, height, hexSize, gridWidth, 
                               leftMargin, topMargin)

        # Create sector info

## Hex system class.
#
#  The hex system class is used to create imagery for a star system to display 
#  in a sector hex grid.
class HexSystem(object):
    ## Hex system class constructor.
    #  @param self    The object pointer.
    #  @param hexSize The hex size to draw the system in [px].
    def __init__(self,
                 hexSize):
        pass


## Sector image class.
#
#  The sector image class is used to create images of an SWN sector.
class SectorImage(object):
    ## Sector image class constructor.
    #  @param self The object pointer.
    #  @param rows              Number of hex rows.
    #  @param cols              Number of hex columns.
    #  @param width             Image width in pixels.
    #  @param topMarginRatio    Top margin ratio relative to height.
    #  @param bottomMarginRatio Bottom margin ratio relative to height.
    #  @param leftMarginRatio   Left margin ratio relative to width.
    #  @param rightMarginRatio  Right margin ratio relative to width.
    def __init__(self,
                 rows,
                 cols,
                 width             = None,
                 topMarginRatio    = None,
                 bottomMarginRatio = None,
                 leftMarginRatio   = None,
                 rightMarginRatio  = None):
        # Check arguments
        self._rows        = exception.arg_check(rows,              int)
        self._cols        = exception.arg_check(cols,              int)
        width             = exception.arg_check(width,             int,   _SECTOR_IMAGE_WIDTH)
        topMarginRatio    = exception.arg_check(topMarginRatio,    float, _SECTOR_TOP_MARGIN_RATIO)
        bottomMarginRatio = exception.arg_check(bottomMarginRatio, float, _SECTOR_BOTTOM_MARGIN_RATIO)
        leftMarginRatio   = exception.arg_check(leftMarginRatio,   float, _SECTOR_LEFT_MARGIN_RATIO)
        rightMarginRatio  = exception.arg_check(rightMarginRatio,  float, _SECTOR_RIGHT_MARGIN_RATIO)

        # Set sector map parameters
        self.set_params(width, topMarginRatio, bottomMarginRatio, leftMarginRatio, rightMarginRatio)
        width      = self._size[0]
        height     = self._size[1]
        hexSize    = self._hexSize
        gridWidth  = self._gridWidth
        leftMargin = self._leftMargin
        topMargin  = self._topMargin

        # Create sector hex map
        self.hexMap = HexMap(rows, cols, width, height, hexSize, gridWidth, leftMargin, topMargin)

    def draw_orbit_maps(self):
        raise Exception('Not implemented yet.')

    def draw_sector_map(self):
        raise Exception('Not implemented yet.')

    def draw_sector_info(self):
        raise Exception('Not implemented yet.')

    ## Set image parameters.
    #  @param self              The object pointer.
    #  @param width             Image width in pixels.
    #  @param topMarginRatio    Top margin ratio relative to height.
    #  @param bottomMarginRatio Bottom margin ratio relative to height.
    #  @param leftMarginRatio   Left margin ratio relative to width.
    #  @param rightMarginRatio  Right margin ratio relative to width.
    def set_params(self,
                   width             = None,
                   topMarginRatio    = None,
                   bottomMarginRatio = None,
                   leftMarginRatio   = None,
                   rightMarginRatio  = None):
        # Check arguments
        width             = exception.arg_check(width,             int,   _SECTOR_IMAGE_WIDTH)
        topMarginRatio    = exception.arg_check(topMarginRatio,    float, _SECTOR_TOP_MARGIN_RATIO)
        bottomMarginRatio = exception.arg_check(bottomMarginRatio, float, _SECTOR_BOTTOM_MARGIN_RATIO)
        leftMarginRatio   = exception.arg_check(leftMarginRatio,   float, _SECTOR_LEFT_MARGIN_RATIO)
        rightMarginRatio  = exception.arg_check(rightMarginRatio,  float, _SECTOR_RIGHT_MARGIN_RATIO)

        # Grid information
        rows = self._rows
        cols = self._cols

        # Margins in pixels
        topMargin    = int(width*topMarginRatio)
        bottomMargin = int(width*bottomMarginRatio)
        leftMargin   = int(width*leftMarginRatio)
        rightMargin  = int(width*rightMarginRatio)

        # Map width
        mapWidth = width - leftMargin - rightMargin

        # Hex sizes
        hexSizeByWidth = float(2.0*mapWidth)/float(3.0*cols+1.0)
        hexSize        = hexSizeByWidth
        hexWidth       = float(hexSize*2.0)
        hexHeight      = float(float(math.sqrt(3.0)/2.0)*float(hexWidth))

        # Map height
        mapHeight = int((math.sqrt(3.0)/2.0)*hexSize*(2.0*rows+1))

        # Height
        height = int(mapHeight + topMargin + bottomMargin)

        # Map bounding box        
        mapTopLeft     = (leftMargin,          topMargin)
        mapTopRight    = (leftMargin+mapWidth, topMargin)
        mapBottomRight = (leftMargin+mapWidth, topMargin+mapHeight)
        mapBottomLeft  = (leftMargin,          topMargin+mapHeight)

        # Drawing specifications
        routeWidth       = int(hexSize*_ROUTE_WIDTH_RATIO)
        routeBlurSize    = routeWidth*_ROUTE_BLUR_SIZE_RATIO
        gridWidth        = int(routeWidth*_GRID_WIDTH_RATIO)
        starDiameter     = int(hexSize*_STAR_DIAMETER_RATIO)
        worldOrbitRadius = int(hexHeight*_WORLD_ORBIT_RADIUS_RATIO)
        worldDiameter    = int(hexSize*_WORLD_DIAMETER_RATIO)
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
        self._topMargin        = topMargin
        self._bottomMargin     = bottomMargin
        self._leftMargin       = leftMargin
        self._rightMargin      = rightMargin
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