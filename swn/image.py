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

import color
import exception
import hexutils
import star

_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Sector Defaults --------------------------------------------------------------
# Size
_SECTOR_IMAGE_WIDTH  = 1500 # px
_SECTOR_IMAGE_SCALE  = 3    # Scale to increase image size for antialiasing

# Margins
_SECTOR_VERTICAL_MARGIN_RATIO   = 0.02
_SECTOR_HORIZONTAL_MARGIN_RATIO = 0.02
# Drawing specifications -------------------------------------------------------
_ANGLE_BETWEEN_WORLDS            = 60
_FACTION_ALPHA                   = 35
_GRID_WIDTH_RATIO                = 2./1500.
_GRID_COLOR                      = color.THEME_GREY
_GRID_ALPHA                      = 200
_IMAGE_BACKGROUND                = os.path.join(_DIR_PATH,'images/starfield.png')
_IMAGE_BACKGROUND_BRIGHTNESS     = 0.8
_INFO_TABLE_TITLE_ROWS           = 3
_ORBIT_X_OFFSET_RATIO            = 1./7.
_ORBIT_Y_OFFSET_RATIO            = 1./15.
_ORBITAL_OBJECT_COLOR_MAP = {
    'cold stone':               color.Color(80,96,119),
    'hot rock':                 color.Color(254,218,124),
    'hydrocarbon astroid belt': color.Color(214,213,147),
    'ice':                      color.Color(207,245,246),
    'icy asteroid belt':        color.Color(207,245,246),
    'rocky':                    color.Color(104,95,78),
    'large gas':                color.Color(165,142,111),
    'medium moon':              color.Color(247,247,247),
    'metal asteroid belt':      color.Color(140,143,147),
    'rocky asteroid belt':      color.Color(104,95,78),
    'small gas':                color.Color(173,216,180),
    'small moon':               color.Color(247,247,247),
    'space station':            color.WHITE}
_ORBITAL_OBJECT_SIZE_RATIO_MAP = {
    'cold stone':               1./5.,
    'hot rock':                 1./5.,
    'hydrocarbon astroid belt': 1./5.,
    'ice':                      1./5.,
    'icy asteroid belt':        1./5.,
    'rocky':                    1./5.,
    'large gas':                7./10.,
    'medium moon':              1./11.,
    'metal asteroid belt':      1./5.,
    'rocky asteroid belt':      1./5.,
    'small gas':                5./10.,
    'small moon':               1./20.,
    'space station':            1./15.}
_PLANET_RING_ANGLE               = 30.*math.pi/180.
_PLANET_RING_RATIO               = 3./10.
_PLANET_RING_GAP_RATIO           = 1./10.
_ROUTE_WIDTH_RATIO               = 1./10.
_ROUTE_BLUR_SIZE_RATIO           = 0.6
_ROUTE_COLOR                     = (179,235,250,100)
_STAR_BLUR_RATIO                 = 1./10.
_STAR_COLOR_MAP = {
    'red':          color.Color(250,191,113),
    'white':        color.Color(205,214,253),
    'light yellow': color.Color(251,248,255),
    'yellow':       color.Color(254,245,230),
    'orange':       color.Color(251,221,186) }
_STAR_HEX_DIAMETER_RATIO         = 1./5.
_STAR_ORBIT_BLUR_RATIO           = 1./75.
_STAR_ORBIT_CENTER_OFFSET_RATIO  = 2./10.
_STAR_ORBIT_DIAMETER_RATIO       = 5.
_STAR_ORBIT_OFFSET_RATIO         = 5./20.
_SYSTEM_COLOR                    = color.LIGHT_GREY
_SYSTEM_MAP_HEIGHT_RATIO         = 1./10.
_SYSTEM_OUTLINE_COLOR            = color.BLACK
_TRIANGLE_LENGTH_RATIO           = 1./6.
_TRIANGLE_MARGIN_RATIO           = 1./40.
_WORLD_ORBIT_RADIUS_RATIO        = 1./3.
_WORLD_DIAMETER_RATIO            = 1./9.
_WORLD_INFO_MARGIN_RATIO         = 1./4.
_WORLD_COLOR                     = color.LIGHT_GREY

# Font specifications
_FONT_FILENAME                   = os.path.join(_DIR_PATH,'fonts/mplus-1m-regular.ttf')
_HEX_FONT_SIZE_RATIO             = 1./6.
_HEX_FONT_COLOR                  = color.THEME_GREY
_HEX_NUM_MARGIN_RATIO            = 1./18.
_INFO_FONT_COLOR                 = color.LIGHT_GREY
_INFO_FONT_SIZE_RATIO            = 1./6.
_LIST_FONT_FILENAME              = _FONT_FILENAME
_SECTOR_FONT_FILENAME            = _FONT_FILENAME
_SYSTEM_NAME_FONT_SIZE_RATIO     = 1./6.5
_SYSTEM_FONT_COLOR               = color.LIGHT_GREY
_SYSTEM_NAME_MARGIN_RATIO        = 1./6.
_TABLE_FONT_SIZE_RATIO           = 2./3.
_TABLE_TITLE_FONT_SIZE_RATIO     = 2.

## Hex class.
#
#  The hex class is used to create imagery for a hex to display in a
#  sector hex grid.
class Hex(object):
    ## Hex class constructor.
    #  @param self    The object pointer.
    #  @param hexSize The hex size to draw the system in [px].
    def __init__(self,
                 hexSize):
        # Check arguments.
        hexSize = exception.arg_check(hexSize, float)
        # Set hex parameters.
        self._set_parameters(hexSize)
        # Blank hex information.
        self.reset()
        # Working image. Leave as None until ready to draw.
        self.bgWorkingImage = None # Background
        self.fgWorkingImage = None # Foreground

    ## Set hex parameters.
    #  @param self The object pointer.
    #  @hexSize    The hex size to draw the system in [px].
    def _set_parameters(self, hexSize):
        self._hexSize = exception.arg_check(hexSize, float)
        # Image size.
        self._width  = int(hexutils.flat_width(self._hexSize))
        self._height = int(hexutils.flat_height(self._hexSize))
        # System data.
        self._systemDiameter = int(hexSize*_STAR_HEX_DIAMETER_RATIO)
        systemFontSize       = int(self._height*_SYSTEM_NAME_FONT_SIZE_RATIO)
        self._systemFont     = pilfont.truetype(_FONT_FILENAME, systemFontSize, encoding="unic")
        self._systemFontMargin = int(self._height*_SYSTEM_NAME_MARGIN_RATIO)
        # World data.
        self._worldDiamater      = int(hexSize*_WORLD_DIAMETER_RATIO)
        self._worldOrbitDiameter = int(self._height*_WORLD_ORBIT_RADIUS_RATIO)
        worldFontSize            = int(self._height*_INFO_FONT_SIZE_RATIO)
        self._worldFont          = pilfont.truetype(_FONT_FILENAME, worldFontSize, encoding="unic")
        self._worldFontMargin    = int(self._hexSize*_WORLD_INFO_MARGIN_RATIO)
        # Vertex info data.
        self._triangleLength = int(hexSize*_TRIANGLE_LENGTH_RATIO)
        self._triangleMargin = int(self._height*_TRIANGLE_MARGIN_RATIO)

    ## Add system information.
    #  @param self The object pointer.
    #  @param _name Color for the system.
    #  @param fillColor Color for the system.
    #  @param outlineColor Color for the system outline.
    def add_system(self, _name, fillColor=None, outlineColor=None):
        # Check arguments.
        self._systemName         = exception.arg_check(_name,        str)
        self._systemColor        = exception.arg_check(fillColor,    color.Color, _SYSTEM_COLOR)
        self._systemOutlineColor = exception.arg_check(outlineColor, color.Color, _SYSTEM_OUTLINE_COLOR)

    ## Add world data.
    #  @param self         The object pointer.
    #  @param text         Display text for the world.
    #  @param textColor    Color for the world display text.
    #  @param fillColor    Color for the world.
    #  @param outlineColor Color for the world outline.
    def add_world(self, text=None, textColor=None, fillColor=None, outlineColor=None):
        # Check arguments
        text         = exception.arg_check(text,      str,         '')
        textColor    = exception.arg_check(fillColor, color.Color, _SYSTEM_FONT_COLOR)
        fillColor    = exception.arg_check(fillColor, color.Color, _WORLD_COLOR)
        outlineColor = exception.arg_check(fillColor, color.Color, _WORLD_COLOR)
        
        # Add world data to list
        self._world.append((text, textColor, fillColor, outlineColor))

    ## Draw hex.
    #  @param self The object pointer.
    def draw(self):
        # Calculate center.
        (cX, cY) = (int(self._width/2), int(self._height/2))

        # Blank image before drawing.
        if not(self.fgWorkingImage is None):
            self.fgWorkingImage.close()
        self.fgWorkingImage = pilimage.new("RGBA", (self._width, self._height))
        if not(self.bgWorkingImage is None):
            self.bgWorkingImage.close()
        self.bgWorkingImage = pilimage.new("RGBA", (self._width, self._height))

        # Draw background.
        bgDrawingImage = pildraw.Draw(self.bgWorkingImage)
        # Draw foreground.
        fgDrawingImage = pildraw.Draw(self.fgWorkingImage)

        # Draw vertex triangles.
        # Draw system.
        if not (self._systemName is None):
            fgDrawingImage.ellipse([(cX-self._systemDiameter/2, cY-self._systemDiameter/2),
                                    (cX+self._systemDiameter/2, cY+self._systemDiameter/2)],
                                   outline = self._systemColorOutline.rgba(),
                                   fill    = self._systemColor.rgba())
            
            # Get system name text size.
            nameWidth, nameHeight = fgDrawingImage.textsize(self._systemName,
                                                            font=self._systemFont)
            # System text center position.
            nameTextCenter = (int(cX-nameWidth/2.), int(cY-nameHeight/2.+self._systemFontMargin))
            # Draw system name text.
            fgDrawingImage.text(nameTextCenter,
                                self._systemName.upper(),
                                fill=_SYSTEM_FONT_COLOR.rgba(),
                                font=self._systemFont)
        # Draw worlds.
        numWorlds = len(self._world)
        for wIndex in xrange(numWorlds):
            # Get world info.
            wText         = self._world[wIndex][0]
            wTextColor    = self._world[wIndex][1]
            wFillColor    = self._world[wIndex][2]
            wOutlineColor = self._world[wIndex][3]
            # Determine world position.
            # Angle (0 is right, 90 is up)
            angleDeg  = float(90)
            angleDeg += (float(_ANGLE_BETWEEN_WORLDS)/2.)*float(numWorlds-1.)
            angleDeg += -float(_ANGLE_BETWEEN_WORLDS)*float(wIndex)
            # X and Y components of orbit radius
            cosRadius = int(math.cos(angleDeg*math.pi/180.)*self._worldOrbitDiameter/2.)
            sinRadius = int(math.sin(angleDeg*math.pi/180.)*self._worldOrbitDiameter/2.)
            # World center position
            worldCenter = (int(cX+cosRadius), int(cY-sinRadius))
            # Draw world.
            fgDrawingImage.ellipse([(worldCenter[0]-self._worldDiamater/2, int(worldCenter[1]-self._worldDiamater/2)),
                                    (worldCenter[0]+self._worldDiamater/2, int(worldCenter[1]+self._worldDiamater/2))],
                                   outline = wOutlineColor.rgba(),
                                   fill    = wFillColor.rgba())
            # Get text size.
            textWidth, textHeight = fgDrawingImage.textsize(wText,font=self._worldFont)
            # X and Y components of orbit text radius.
            cosRadius = int(math.cos(angleDeg*math.pi/180.)*(self._worldOrbitDiameter/2.+self._worldFontMargin))
            sinRadius = int(math.sin(angleDeg*math.pi/180.)*(self._worldOrbitDiameter/2.+self._worldFontMargin))
            # World text center position.
            worldTextCenter = (int(cX+cosRadius), int(cY-sinRadius))
            # Draw world text.
            fgDrawingImage.text((worldTextCenter[0]-textWidth/2,worldTextCenter[1]-textHeight/2),
                                wText, 
                                fill=wTextColor.rgba(),
                                font=self._worldFont)

    ## Reset hex data.
    #  @param self The object pointer.
    def reset(self):
        # Blank name
        self._systemName = None
        # Blank system
        self._systemColor = color.NONE
        self._systemColorOutline = color.NONE
        # Blank each vertex
        self._vertexColors = [color.NONE] * 6
        # Blank worlds
        self.reset_worlds()

    ## Reset world data.
    def reset_worlds(self):
        self._world = list()

    ## Resize hex.
    #  @param self    The object pointer.
    #  @param hexSize The hex size to draw the system in [px].
    def resize(self, hexSize):
        # Check arguments
        exception.arg_check(hexSize, float)
        # Set hex parameters.
        self._set_params(self._hexSize)

    ## Set vertex color.
    #  @param self The object pointer.
    #  @param Color for the vertex.
    def set_vertex_color(self, vertex, _color):
        # Check arguments
        vertex = exception.arg_check(vertex, int)
        vertex = exception.arg_range_check(vertex, 0, 5)
        _color = exception.arg_check(_color, color.Color)
        self._vertexColors[vertex] = _color

## Hex grid class.
#
#  The hex grid class is used to create a hex grid image to display in the 
#  sector hex grid map.
class HexGrid(object):
    ## Hex grid class constructor.
    #  @param self             The object pointer.
    #  @param majorRow         Major row of sector.
    #  @param majorCol         Major column of sector.
    #  @param rows             Number or rows in the grid.
    #  @param cols             Number of columns in the grid.
    #  @param width            Width of the grid image [px].
    #  @param height           Height of the grid image [px].
    #  @param hexSize          Size of the grid hexes [px].
    #  @param verticalMargin   Vertical margin of the grid image [px].
    #  @param horizontalMargin Horizontal margin of the grid image [px].
    #  @param gridColor        Color of gridlines.
    def __init__(self,
                 majorRow,
                 majorCol,
                 rows,
                 cols,
                 width,
                 height,
                 hexSize,
                 verticalMargin   = None,
                 horizontalMargin = None,
                 gridColor        = None):
        # Check arguments
        self._majorRow         = exception.arg_check(majorRow,         int)
        self._majorCol         = exception.arg_check(majorCol,         int)
        self._rows             = exception.arg_check(rows,             int)
        self._cols             = exception.arg_check(cols,             int)
        self._width            = exception.arg_check(width,            int)
        self._height           = exception.arg_check(height,           int)
        self._hexSize          = exception.arg_check(hexSize,          float)
        self._verticalMargin   = exception.arg_check(verticalMargin,   int, 0)
        self._horizontalMargin = exception.arg_check(horizontalMargin, int, 0)
        self._gridColor        = exception.arg_check(gridColor,        color.Color, _GRID_COLOR)

        # Set grid parameters.
        self._set_params(self._width, 
                         self._height, 
                         self._hexSize,  
                         self._verticalMargin, 
                         self._horizontalMargin,
                         self._gridColor)

        # Working image. Leave as None until ready to draw.
        self.workingImage = None

    ## Draw hex grid.
    #  @param self The object pointer.
    def draw(self):
        # Blank image before drawing
        if not (self.workingImage is None):
            self.workingImage.close()
        self.workingImage = pilimage.new("RGBA", (self._width,self._height))
        
        # Create drawing image
        drawingImage = pildraw.Draw(self.workingImage)
        # Draw grid vertex lines
        fillColor = self._gridColor.rgba(255)
        lineWidth = int(_GRID_WIDTH_RATIO*self._width)
        for gl in self._gridLines:
            drawingImage.line([gl[0], gl[1]], fill=fillColor, width=lineWidth)
        # Draw hex number text
        #    For each row
        for row in xrange(self._rows):
            # For each column
            for col in xrange(self._cols):
                # Center of hex in integer pixels
                (xc, yc) = hexutils.odd_q_center(self._hexSize, row, col)
                (xc, yc) = (int(xc), int(yc))
                # Offset centers by margins
                (xc, yc) = (xc + self._horizontalMargin, yc + self._verticalMargin)
                # Hex number text
                hexNum = '{mCol}{col}{mRow}{row}'.format(mCol = self._majorCol,
                                                         col  = col,
                                                         mRow = self._majorRow,
                                                         row  = row)
                # Hex number text size
                w, h = drawingImage.textsize(hexNum, font=self._font)
                # Draw hex number text
                drawingImage.text((xc-w/2, 
                                   yc+self._hexHeight/2 - h - _HEX_NUM_MARGIN_RATIO*self._hexHeight),
                                  hexNum, 
                                  fill=_HEX_FONT_COLOR.rgba(), 
                                  font=self._font)

    ## Set grid parameters.
    #  @param self             The object pointer.
    #  @param width            Width of the grid image [px].
    #  @param height           Height of the grid image [px].
    #  @param hexSize          Size of the grid hexes [px].
    #  @param verticalMargin   Vertical margin of the grid image [px].
    #  @param horizontalMargin Horizontal margin of the grid image [px].
    #  @param gridColor        Color of gridlines.
    def _set_params(self,
                    width            = None,
                    height           = None,
                    hexSize          = None,
                    verticalMargin   = None,
                    horizontalMargin = None,
                    gridColor        = None):
        # Check arguments
        self._width            = exception.arg_check(width,            int,         self._width)
        self._height           = exception.arg_check(height,           int,         self._height)
        self._hexSize          = exception.arg_check(hexSize,          float,       self._hexSize)
        self._verticalMargin   = exception.arg_check(verticalMargin,   int,         self._verticalMargin)
        self._horizontalMargin = exception.arg_check(horizontalMargin, int,         self._horizontalMargin)
        self._gridColor        = exception.arg_check(gridColor,        color.Color, self._gridColor)

        # Calculate hex height
        self._hexHeight = hexutils.flat_height(hexSize)

        # Grid info
        self._gridWidth = int(self._hexSize*_GRID_WIDTH_RATIO)

        # Hex font
        fontSize = int(_HEX_FONT_SIZE_RATIO*hexutils.flat_height(hexSize))
        self._font = pilfont.truetype(_FONT_FILENAME, fontSize, encoding="unic")
        
        # Set of lines to draw between vertices
        self._gridLines = list()
        # For each row
        for row in xrange(self._rows):
            # For each column
            for col in xrange(self._cols):
                # Center of hex in integer pixels
                (xc, yc) = hexutils.odd_q_center(self._hexSize, row, col)
                (xc, yc) = (int(xc), int(yc))
                # Offset centers by margins
                (xc, yc) = (xc + self._horizontalMargin, yc + self._verticalMargin)
                # Generate pairs of vertices to draw
                for vertex in xrange(0,6):
                    # Get vertex positions in integer pixels
                    (x0, y0) = hexutils.flat_vertex(self._hexSize, vertex)
                    (x1, y1) = hexutils.flat_vertex(self._hexSize, vertex+1)
                    # Convert vertices to integer pixels
                    (x0, y0) = (int(x0), int(y0))
                    (x1, y1) = (int(x1), int(y1))
                    # Add pair of vertices to list if they aren't already
                    if (((x0+xc, y0+yc), (x1+xc, y1+yc)) not in self._gridLines) and \
                       (((x1+xc, y1+yc), (x0+xc, y0+yc)) not in self._gridLines):
                        self._gridLines.append(((x0+xc, y0+yc), (x1+xc, y1+yc)))

## Hex map class.
#
#  The hex map class is used to create a sector hex map.
class HexMap(object):
    ## Hex sector class constructor.
    #  @param self             The object pointer.
    #  @param majorRow         Major row of sector.
    #  @param majorCol         Major column of sector.
    #  @param rows             Number of hex rows (odd-q).
    #  @param cols             Number of hex columns (odd-q).
    #  @param width            The width of the sector image [px].
    #  @param height           The height of the sector image [px].
    #  @param hexSize          The hex size to draw the system in [px].
    #  @param verticalMargin   Left margin of the grid image [px].
    #  @param horizontalMargin Top margin of the grid image [px].
    #  @param gridColor        Color of gridlines.
    #  @param background       Background image.
    def __init__(self,
                 majorRow,
                 majorCol,
                 rows,
                 cols,
                 width,
                 height,
                 hexSize,
                 verticalMargin    = None,
                 horizontalMargin  = None,
                 gridColor         = None,
                 background        = None):
        # Check arguments.
        exception.arg_check(majorRow, int)
        exception.arg_check(majorCol, int)
        exception.arg_check(rows,     int)
        exception.arg_check(cols,     int)
        self._width            = exception.arg_check(width,            int)
        self._height           = exception.arg_check(height,           int)
        self._hexSize          = exception.arg_check(hexSize,          float)
        self._verticalMargin   = exception.arg_check(verticalMargin,   int, 0)
        self._horizontalMargin = exception.arg_check(horizontalMargin, int, 0)
        self._gridColor        = exception.arg_check(gridColor,        color.Color, _GRID_COLOR)
        self._background       = exception.arg_check(background,       pilimage.Image, pilimage.new("RGBA", (width,height), color=color.BLACK.rgba()))

        # Set map size.
        self._set_params(self._width, 
                         self._height, 
                         self._verticalMargin, 
                         self._horizontalMargin, 
                         self._gridColor, 
                         self._background)

        # Working image. Leave as None until ready to draw.
        self._workingImage = None

        # Create sector grid
        self.hexGrid = HexGrid(majorRow, majorCol, rows, cols, width, height, 
                               hexSize, verticalMargin, horizontalMargin)

        # Create sector routes
        #self.routes = Routes(

        # Create sector info
        self.hexInfo = dict()
        # For each row
        for row in xrange(rows):
            # For each column
            for col in xrange(cols):
                self.hexInfo[(row,col)] = Hex(hexSize)

    ## Set hex map parameters.
    #  @param self             The object pointer.
    #  @param width            Hex map width in pixels.
    #  @param height           Hex map height in pixels.
    #  @param verticalMargin   Left margin in pixels.
    #  @param horizontalMargin Top margin in pixels.
    #  @param gridColor        Color of gridlines.
    #  @param background       Background image.
    def _set_params(self, 
                    width            = None, 
                    height           = None, 
                    verticalMargin   = None, 
                    horizontalMargin = None, 
                    gridColor        = None, 
                    background       = None):
        # Check arguments
        self._width            = exception.arg_check(width,            int,            self._width)
        self._height           = exception.arg_check(height,           int,            self._height)
        self._verticalMargin   = exception.arg_check(verticalMargin,   int,            self._verticalMargin)
        self._horizontalMargin = exception.arg_check(horizontalMargin, int,            self._horizontalMargin)
        self._gridColor        = exception.arg_check(gridColor,        color.Color,    self._gridColor)
        self._background       = exception.arg_check(background,       pilimage.Image, self._background)

    ## Draw hex map.
    def draw(self):
        # Blank image before drawing
        if not (self._workingImage is None):
            self._workingImage.close()
        self._workingImage = pilimage.new("RGBA", (self._width, self._height))
        # Draw layers ----------------------------------------------------------
        # Draw sector grid
        self.hexGrid.draw()
        # Draw sector routes
        #self.routes.draw()
        # Draw sector system info
        for (row, col) in self.hexInfo.iterkeys():
            self.hexInfo[(row,col)].draw()

        # Combine layers -------------------------------------------------------
        # Paste sector grid
        self._workingImage.paste(self.hexGrid.workingImage,mask=self.hexGrid.workingImage)
        # Paste sector system info backgrounds
        #for each hex
        #self.workingImage.paste(self.systemInfo.bgWorkingImage,mask=self.hexGrid.workingImage)
        # Paste sector routes
        #self.workingImage.paste(self.routes.workingImage,mask=self.hexGrid.workingImage)
        # Paste sector system info foregrounds
        for (row, col) in self.hexInfo.iterkeys():
            # Get hex centers
            (cX, cY) = hexutils.odd_q_center(self._hexSize, row, col)
            # Round to integers
            (cX, cY) = (int(cX), int(cY))
            # Offset by margins
            (cX, cY) = (cX+self._horizontalMargin, cY+self._verticalMargin)
            # Get width
            hexWidth  = int(hexutils.flat_width(self._hexSize))
            hexHeight = int(hexutils.flat_height(self._hexSize))
            self._workingImage.paste(self.hexInfo[(row,col)].fgWorkingImage,
                                     box=(cX-hexWidth/2, cY-hexHeight/2),
                                     mask=self.hexInfo[(row,col)].fgWorkingImage)

    ## Set hex map size.
    def resize(self, width, height, verticalMargin, horizontalMargin):
        # Check arguments
        width            = exception.arg_check(width,            int)
        height           = exception.arg_check(height,           int)
        verticalMargin   = exception.arg_check(verticalMargin,   int)
        horizontalMargin = exception.arg_check(horizontalMargin, int)

        # Set map size.
        self._set_params(width, height, verticalMargin, horizontalMargin)

        # Set grid size.
        self.hexGrid.resize(hexSize)

        # Set hex info sizes.

    ## Save hex map to file.
    def save(self, path):
        # Check arguments
        path = exception.arg_check(path, str)

        # Draw image if it hasn't been
        if self._workingImage is None:
            self.draw()

        # Resize background image.
        # Get scale of actual image to background image.
        bgScale  = float(self._height)/float(self._background.height)
        # Calculate width assuming resizing background image height to actual 
        # image height.
        bgWidth  = int(math.ceil(bgScale*self._background.width))
        # Calculate number of times background image is requred to tile to fit
        # width.
        bgTile   = int(math.ceil(float(self._width)/float(bgWidth)))
        # Resize background image to match actual image height.
        bgResize = self._background.resize((bgWidth,self._height), pilimage.LANCZOS)

        # Create image to save
        saveImage = pilimage.new('RGBA', (self._width, self._height))

        # Paste background
        for tile in xrange(bgTile):
            saveImage.paste(bgResize, box=((tile)*bgWidth,0), mask=bgResize)

        # Paste working image
        saveImage.paste(self._workingImage, box=(0,0), mask=self._workingImage)

        # Resize/scale down with antialiasing to smooth jagged lines
        saveImage = saveImage.resize((self._width/_SECTOR_IMAGE_SCALE, 
                                      self._height/_SECTOR_IMAGE_SCALE),
                                     pilimage.LANCZOS)

        # Save image
        saveImage.save(path)

## Sector information table class.
#
#  The sector information table class is used to create images of an SWN sector.
class InfoTable(object):
    ## Sector information table image class constructor.
    #  @param self             The object pointer.
    #  @param sectorName       Name of the sector.
    #  @param height           Hex map height in pixels.
    #  @param verticalMargin   Vertical margin in pixels.
    #  @param horizontalMargin Horizontal margin in pixels.
    #  @param background       Background image.
    def __init__(self, 
                 sectorName, 
                 height, 
                 verticalMargin   = None,
                 horizontalMargin = None,
                 background       = None):
        # Check arguments.
        self._sectorName       = exception.arg_check(sectorName,       str)
        self._height           = exception.arg_check(height,           int)
        self._verticalMargin   = exception.arg_check(verticalMargin,   int, 0)
        self._horizontalMargin = exception.arg_check(horizontalMargin, int, 0)
        self._background       = exception.arg_check(background,       pilimage.Image, pilimage.new("RGBA", (height,height), color=color.BLACK.rgba()))

        # Set parameters.
        self._set_params(self._height,
                         self._verticalMargin,
                         self._horizontalMargin)
        
        # Dictionary of information about each hex.
        self._hexInfo    = dict()

        # Working image. Leave as None until ready to draw.
        self._workingImage = None

    ## Set information table image parameters.
    #  @param self             The object pointer.
    #  @param height           Hex map height in pixels.
    #  @param verticalMargin   Top margin in pixels.
    #  @param horizontalMargin Bottom margin in pixels.
    def _set_params(self, 
                    height           = None,
                    verticalMargin   = None,
                    horizontalMargin = None):
        # Check arguments
        self._height           = exception.arg_check(height,           int, self._height)
        self._verticalMargin   = exception.arg_check(verticalMargin,   int, self._verticalMargin)
        self._horizontalMargin = exception.arg_check(horizontalMargin, int, self._horizontalMargin)

    #  @param majorRow   Major row of sector.
    #  @param majorCol   Major column of sector.
    def add_world(self,
                  majorRow,
                  majorCol,
                  hRow, 
                  hCol, 
                  systemName,
                  worldName,
                  techLevel,
                  atmosphere,
                  biosphere, 
                  population,
                  populationAlt,
                  tags,
                  temperature,
                  advisory=None):

        # Check arguments.
        exception.arg_check(majorRow,       int)
        exception.arg_range_check(majorRow, 0, 9)
        exception.arg_check(majorCol,       int)
        exception.arg_range_check(majorCol, 0, 9)
        exception.arg_check(hRow,           int)
        exception.arg_range_check(hRow,     0, 9)
        exception.arg_check(hCol,           int)
        exception.arg_range_check(hCol,     0, 9)
        exception.arg_check(systemName,     str)
        exception.arg_check(worldName,      str)
        exception.arg_check(techLevel,      str)
        exception.arg_check(atmosphere,     str)
        exception.arg_check(biosphere,      str)
        exception.arg_check(population,     str)
        exception.arg_check(populationAlt,  str)
        exception.arg_check(tags,           list)
        for t in tags:
            exception.arg_check(t,          str)
        exception.arg_check(temperature,    str)
        exception.arg_check(advisory,       list, list())
        for a in advisory:
            exception.arg_check(a,          str)

        # Calculate hex string
        hexString = '{mc}{hc}{mr}{hr}'.format(mc=majorCol,
                                              hc=hCol,
                                              mr=majorRow,
                                              hr=hRow)

        # Check to see if any system in hex.
        tableKey = (hexString, systemName)
        if (not self._hexInfo.has_key(tableKey)):
            self._hexInfo[tableKey] = dict()
        # Add world to hex system.
        self._hexInfo[tableKey][worldName] = {'hex':           hexString,
                                              'system':        systemName,
                                              'world':         worldName,
                                              'techLevel':     techLevel,
                                              'atmosphere':    atmosphere,
                                              'biosphere':     biosphere,
                                              'temperature':   temperature,
                                              'population':    population,
                                              'populationAlt': populationAlt,
                                              'tags':          ', '.join(tags),
                                              'advisory':      ', '.join(advisory)}

    def draw(self, gm=False):
        # Blank image before drawing
        if not (self._workingImage is None):
            self._workingImage.close()

        # Number of worlds.
        numWorlds = 0
        for hexKey in self._hexInfo.iterkeys():
            numWorlds += len(self._hexInfo[hexKey])

        # Number of rows.
        #    # of title rows + 1 heading row + # of worlds.
        numRows = _INFO_TABLE_TITLE_ROWS + 1 + numWorlds

        # Drawable info table height.
        infoHeight = self._height - 2*self._verticalMargin

        # Calculate row height based on the number of worlds.
        rowHeight = int(float(infoHeight)/float(numRows))
        # For a small number of worlds, lower the row height so the image isn't
        # really wide.
        if (numWorlds < 15):
            rowHeight = int(float(infoHeight)/float(40))

        # Determine if there are any advisories to show.
        advisoryFlag = False
        # For each system hex.
        for hexKey in self._hexInfo.iterkeys():
            hexDict = self._hexInfo[hexKey]
            # For each world.
            for worldKey in hexDict.iterkeys():
                # Get world info
                worldDict = hexDict[worldKey]
                if (len(worldDict['advisory']) > 0):
                    advisoryFlag = True
                    break
            if (advisoryFlag):
                break

        # Default column width calculations to be based on the heading titles.
        # Add 2 to each length for a space on either side of value.
        maxIndex  = len('#')+2
        maxHex    = len('0000')+2
        maxSystem = len('System')+2
        maxWorld  = len('World')+2
        maxTL     = len('TL')+2
        maxAtmo   = len('Atmosphere')+2
        maxBio    = len('Biosphere')+2
        maxTemp   = len('Temperature')+2
        maxPop    = len('Population')+2
        maxPopAlt = len('Pop. Alt.')+2
        if (gm):
            maxTags   = len('Tags')+2
        if (advisoryFlag):
            maxAdvis  = len('Advisory')+2

        # For each system hex.
        worldCount = 0
        for hexKey in self._hexInfo.iterkeys():
            hexDict = self._hexInfo[hexKey]
            # For each world.
            for worldKey in hexDict.iterkeys():
                worldCount += 1
                # Get world info
                worldDict = hexDict[worldKey]
                # Add 2 to each length for a space on either side of value.
                maxIndex  = max(maxIndex,  len(str(worldCount))+2)
                maxSystem = max(maxSystem, len(worldDict['system'])+2)
                maxWorld  = max(maxWorld,  len(worldDict['world'])+2)
                maxTL     = max(maxTL,     len(worldDict['techLevel'])+2)
                maxAtmo   = max(maxAtmo,   len(worldDict['atmosphere'])+2)
                maxBio    = max(maxBio,    len(worldDict['biosphere'])+2)
                maxTemp   = max(maxTemp,   len(worldDict['temperature'])+2)
                maxPop    = max(maxPop,    len(worldDict['population'])+2)
                maxPopAlt = max(maxPopAlt, len(str(worldDict['populationAlt']))+2)
                if (gm):
                    maxTags   = max(maxTags,   len(worldDict['tags'])+2)
                if (advisoryFlag):
                    maxAdvis  = max(maxAdvis,  len(worldDict['advisory'])+2)

        # Total row columns.
        maxRow  = maxIndex + maxHex + maxSystem + maxWorld + maxTL + maxAtmo
        maxRow += maxBio + maxTemp + maxPop + maxPopAlt
        if (gm):
            maxRow += maxTags
        if (advisoryFlag):
            maxRow += maxAdvis

        # Column fractions.
        indexFraction  = float(maxIndex)/float(maxRow)
        hexFraction    = float(maxHex)/float(maxRow)
        systemFraction = float(maxSystem)/float(maxRow)
        worldFraction  = float(maxWorld)/float(maxRow)
        tlFraction     = float(maxTL)/float(maxRow)
        atmoFraction   = float(maxAtmo)/float(maxRow)
        bioFraction    = float(maxBio)/float(maxRow)
        tempFraction   = float(maxTemp)/float(maxRow)
        popFraction    = float(maxPop)/float(maxRow)
        popAltFraction = float(maxPopAlt)/float(maxRow)
        if (gm):
            tagsFraction   = float(maxTags)/float(maxRow)
        if (advisoryFlag):
            advisFraction  = float(maxAdvis)/float(maxRow)

        # Title font.
        titleFontSize = int(rowHeight*_TABLE_TITLE_FONT_SIZE_RATIO)
        titleFont     = pilfont.truetype(_SECTOR_FONT_FILENAME, titleFontSize, encoding="unic")

        # Text font.
        listFontSize = int(rowHeight*_TABLE_FONT_SIZE_RATIO)
        listFont     = pilfont.truetype(_LIST_FONT_FILENAME, listFontSize, encoding="unic")

        # Temporary working image to use texsize for calculations
        self._workingImage = pilimage.new("RGBA", (25, 25))
        drawingImage = pildraw.Draw(self._workingImage)

        # Font character size.
        wChar,hChar  = drawingImage.textsize('|',font=listFont)
        # Font text margin.
        listFontMargin = (rowHeight-hChar)/2.0

        # List width.
        listWidth = maxRow*drawingImage.textsize('A',font=listFont)[0]
        # Image width.
        self._width = listWidth + 2*self._horizontalMargin

        # Prepare drawing image.
        self._workingImage = pilimage.new("RGBA", (self._width, self._height))
        drawingImage = pildraw.Draw(self._workingImage)

        # Draw heading background.
        # Add 1 to fill in background of title and heading names.
        titleBackgroundHeight   = rowHeight*(_INFO_TABLE_TITLE_ROWS)
        headingBackgroundHeight = titleBackgroundHeight + rowHeight
        drawingImage.rectangle([(self._horizontalMargin,
                                 self._verticalMargin),
                                (self._horizontalMargin+listWidth,
                                 self._verticalMargin+headingBackgroundHeight)],
                               fill=_INFO_FONT_COLOR.rgba(50))

        # Draw sector name.
        wSectorName, hSectorName = drawingImage.textsize(self._sectorName, font=titleFont)
        drawingImage.text((int(self._horizontalMargin+(listWidth-wSectorName)/2.0),
                           int(self._horizontalMargin+(rowHeight*3.0*0.85-hSectorName)/2.0)),
                          self._sectorName,
                          fill=_INFO_FONT_COLOR.rgba(),
                          font=titleFont)

        # Calculate pixel offsets for each column line.
        columnOffsets = list()
        columnOffsets.append(float(self._horizontalMargin)/float(listWidth))
        columnOffsets.append(indexFraction)
        columnOffsets.append(hexFraction)
        columnOffsets.append(systemFraction)
        columnOffsets.append(worldFraction)
        columnOffsets.append(tlFraction)
        columnOffsets.append(atmoFraction)
        columnOffsets.append(bioFraction)
        columnOffsets.append(tempFraction)
        columnOffsets.append(popFraction)
        columnOffsets.append(popAltFraction)
        if (gm):
            columnOffsets.append(tagsFraction)
        if (advisoryFlag):
            columnOffsets.append(advisFraction)
        # Initialize current pixel offsets for drawing column lines.
        currentXOffset = 0
        currentYOffset = self._verticalMargin + titleBackgroundHeight
        # Draw each column line.
        for co in columnOffsets:
            # Update x offset for this column.
            currentXOffset += int(co*listWidth)
            # Draw line.
            drawingImage.line([(currentXOffset, currentYOffset),
                               (currentXOffset, currentYOffset+rowHeight*(worldCount+1))],
                              fill=_GRID_COLOR.rgba(),
                              width=int(_GRID_WIDTH_RATIO*self._width))
            # Draw title side borders.
            if (co is columnOffsets[0]) or (co is columnOffsets[len(columnOffsets)-1]):
                drawingImage.line([(currentXOffset, self._verticalMargin),
                                   (currentXOffset, currentYOffset)],
                                  fill=_GRID_COLOR.rgba(),
                                  width=int(_GRID_WIDTH_RATIO*self._width))

        # Initialize current pixel offsets for drawing row lines.
        currentXOffset = self._horizontalMargin
        currentYOffset = self._verticalMargin
        # Draw top border line.
        drawingImage.line([(currentXOffset,                   currentYOffset),
                           (self._horizontalMargin+listWidth, currentYOffset)],
                          fill=_GRID_COLOR.rgba(),
                          width=int(_GRID_WIDTH_RATIO*self._width))
        # Move offset to top of heading row.
        currentYOffset += titleBackgroundHeight
        # Draw heading row line.
        drawingImage.line([(currentXOffset,                   currentYOffset),
                           (self._horizontalMargin+listWidth, currentYOffset)],
                          fill=_GRID_COLOR.rgba(),
                          width=int(_GRID_WIDTH_RATIO*self._width))
        # Draw world index heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'#'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int((indexFraction)*listWidth)
        # Draw hex heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'Hex'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(hexFraction*listWidth)
        # Draw system heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'System'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(systemFraction*listWidth)
        # Draw world heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'World'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(worldFraction*listWidth)
        # Draw TL heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'TL'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(tlFraction*listWidth)
        # Draw atmosphere heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'Atmosphere'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(atmoFraction*listWidth)
        # Draw temperature heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'Temperature'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(bioFraction*listWidth)
        # Draw biosphere heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'Biosphere'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(tempFraction*listWidth)
        # Draw population heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'Population'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(popFraction*listWidth)
        # Draw population alternate heading.
        drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                          ' '+'Pop. Alt.'+' ',
                          fill=_INFO_FONT_COLOR.rgba(), 
                          font=listFont)
        currentXOffset += int(popAltFraction*listWidth)
        if (gm):
            # Draw tags heading.
            drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                              ' '+'Tags'+' ',
                              fill=_INFO_FONT_COLOR.rgba(), 
                              font=listFont)
            currentXOffset += int(tagsFraction*listWidth)
        if (advisoryFlag):
            # Draw advisory heading.
            drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                              ' '+'Advisory'+' ',
                              fill=_INFO_FONT_COLOR.rgba(), 
                              font=listFont)
        # Update offsets.
        currentXOffset = self._horizontalMargin
        currentYOffset += rowHeight
        # For each system hex.
        worldCount = 0
        for hexKey in sorted(self._hexInfo.iterkeys(), key=lambda key: key[0]):
            hexDict = self._hexInfo[hexKey]
            # Draw hex and system part of row line.
            drawingImage.line([(currentXOffset+int(indexFraction*listWidth), 
                                currentYOffset),
                               (currentXOffset+int((indexFraction+hexFraction+systemFraction)*listWidth), 
                                currentYOffset)],
                              fill=_GRID_COLOR.rgba(),
                              width=int(_GRID_WIDTH_RATIO*self._width))
            # Draw hex.
            drawingImage.text((currentXOffset+int(indexFraction*listWidth), 
                              currentYOffset+int(rowHeight*len(hexDict.keys())/2.)-int(rowHeight/2.)+listFontMargin), 
                                  ' '+hexKey[0]+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
            # Draw system.
            drawingImage.text((currentXOffset+int((indexFraction+hexFraction)*listWidth), 
                              currentYOffset+int(rowHeight*len(hexDict.keys())/2.)-int(rowHeight/2.)+listFontMargin), 
                                  ' '+hexKey[1]+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
            # For each world.
            for worldKey in hexDict.iterkeys():
                worldCount += 1
                # Draw left side of row line.
                drawingImage.line([(currentXOffset,                              currentYOffset),
                                   (currentXOffset+int(indexFraction*listWidth), currentYOffset)],
                                  fill=_GRID_COLOR.rgba(),
                                  width=int(_GRID_WIDTH_RATIO*self._width))
                currentXOffset += int((indexFraction+hexFraction+systemFraction)*listWidth)
                # Draw right side row line.
                drawingImage.line([(currentXOffset,                   currentYOffset),
                                   (self._horizontalMargin+listWidth, currentYOffset)],
                                  fill=_GRID_COLOR.rgba(),
                                  width=int(_GRID_WIDTH_RATIO*self._width))
                currentXOffset = self._horizontalMargin
                # Draw world index.
                drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                  ' '+str(worldCount).rjust(maxIndex-2)+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
                currentXOffset += int((indexFraction+hexFraction+systemFraction)*listWidth)
                # Draw world.
                drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                  ' '+self._hexInfo[hexKey][worldKey]['world']+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
                currentXOffset += int(worldFraction*listWidth)
                # Draw TL.
                drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                  ' '+self._hexInfo[hexKey][worldKey]['techLevel']+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
                currentXOffset += int(tlFraction*listWidth)
                # Draw atmosphere.
                drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                  ' '+self._hexInfo[hexKey][worldKey]['atmosphere']+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
                currentXOffset += int(atmoFraction*listWidth)
                # Draw biosphere.
                drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                  ' '+self._hexInfo[hexKey][worldKey]['biosphere']+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
                currentXOffset += int(bioFraction*listWidth)
                # Draw temperature.
                drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                  ' '+self._hexInfo[hexKey][worldKey]['temperature']+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
                currentXOffset += int(tempFraction*listWidth)
                # Draw population.
                drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                  ' '+self._hexInfo[hexKey][worldKey]['population']+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
                currentXOffset += int(popFraction*listWidth)
                # Draw population alternate.
                drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                  ' '+str(self._hexInfo[hexKey][worldKey]['populationAlt']).rjust(maxPopAlt-2)+' ', 
                                  fill=_INFO_FONT_COLOR.rgba(), 
                                  font=listFont)
                currentXOffset += int(popAltFraction*listWidth)
                if (gm):
                    # Draw tags.
                    drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                      ' '+self._hexInfo[hexKey][worldKey]['tags']+' ', 
                                      fill=_INFO_FONT_COLOR.rgba(), 
                                      font=listFont)
                    currentXOffset += int(tagsFraction*listWidth)
                if (advisoryFlag):
                    # Draw advisory.
                    drawingImage.text((currentXOffset, currentYOffset+listFontMargin), 
                                      ' '+self._hexInfo[hexKey][worldKey]['advisory']+' ', 
                                      fill=_INFO_FONT_COLOR.rgba(), 
                                      font=listFont)
                    currentXOffset += int(advisFraction*listWidth)

                # Update offsets.
                currentXOffset  = self._horizontalMargin
                currentYOffset += rowHeight
        # Draw bottom border line.
        drawingImage.line([(currentXOffset,                   currentYOffset),
                           (self._horizontalMargin+listWidth, currentYOffset)],
                          fill=_GRID_COLOR.rgba(),
                          width=int(_GRID_WIDTH_RATIO*self._width))

    ## Resize info table.
    #
    def resize(self, height):
        # Check arguments.
        exception.arg_check(height, int)
        # Set parameters.
        self._set_params(height)

    ## Save info table to file.
    def save(self, path):
        # Check arguments
        path = exception.arg_check(path, str)

        # Draw image if it hasn't been
        if self._workingImage is None:
            self.draw()

        # Resize background image.
        # Get scale of actual image to background image.
        bgScale  = float(self._height)/float(self._background.height)
        # Calculate width assuming resizing background image height to actual 
        # image height.
        bgWidth  = int(math.ceil(bgScale*self._background.width))
        # Calculate number of times background image is requred to tile to fit
        # width.
        bgTile   = int(math.ceil(float(self._width)/float(bgWidth)))
        # Resize background image to match actual image height.
        bgResize = self._background.resize((bgWidth,self._height), pilimage.LANCZOS)

        # Create image to save
        saveImage = pilimage.new('RGBA', (self._width, self._height))

        # Paste background
        for tile in xrange(bgTile):
            saveImage.paste(bgResize, box=((tile)*bgWidth,0), mask=bgResize)

        # Paste working image
        saveImage = pilimage.alpha_composite(saveImage, self._workingImage)

        # Resize/scale down with antialiasing to smooth jagged lines
        saveImage = saveImage.resize((self._width/_SECTOR_IMAGE_SCALE, 
                                      self._height/_SECTOR_IMAGE_SCALE),
                                     pilimage.LANCZOS)

        # Save image
        saveImage.save(path)

## Orbit map image class.
#
# The orbit map image class is used to create images of orbit maps.
class OrbitMap(object):

    class Belt(object):
        def __init__(self,
                     sizeRatio,
                     _color):
            # Check arguments.
            self.sizeRatio  = exception.arg_check(sizeRatio, float)
            # Belt color.
            self.color      = exception.arg_check(_color, color.Color)

    class Sphere(object):
        def __init__(self,
                     sizeRatio,
                     _color,
                     rings=None):
            # Check arguments.
            # Sphere size ratio.
            self.sizeRatio = exception.arg_check(sizeRatio, float)
            # Sphere color.
            self.color     = exception.arg_check(_color, color.Color)
            # Does the sphere have rings.
            self.rings     = exception.arg_check(rings, bool, False)

            # Default diameter to size.
            self.diameterRatio = self.sizeRatio
            # Increase size if there are rings
            if (self.rings):
                self.sizeRatio = (1+_PLANET_RING_RATIO)*self.diameterRatio*math.cos(_PLANET_RING_ANGLE)

            # Satellites around sphere.
            self.satellites = list()

    class Star(object):
        def __init__(self,
                     sizeRatio,
                     _color,
                     classification):
            # Check arguments.
            # Star size ratio.
            self.sizeRatio      = exception.arg_check(sizeRatio, float)
            # Star color.
            self.color          = exception.arg_check(_color, color.Color)
            # Spectral classification.
            self.classification = exception.arg_check(classification, str)

            # Star diameter.
            self.diameterRatio   = self.sizeRatio*(1-_STAR_BLUR_RATIO)
            # Star blur radius.
            self.blurRadiusRatio = self.sizeRatio*_STAR_BLUR_RATIO

    class Station(object):
        def __init__(self,
                     sizeRatio,
                     _color=None):
            # Check arguments.
            # Station size ratio.
            self.sizeRatio = exception.arg_check(sizeRatio, float)
            # Station color.
            self.color     = exception.arg_check(_color,    color.Color, _SYSTEM_COLOR)

    ## Orbit map class constructor.
    #  @param self            The object pointer.
    #  @param systemName      Name of system.
    #  @param referenceHeight Reference height of the image in pixels.
    def __init__(self,
                 systemName,
                 referenceHeight):
        # Check arguments.
        # System name.
        self._systemName      = exception.arg_check(systemName,      str)
        # Image reference height.
        self._referenceHeight = exception.arg_check(referenceHeight, int)

        # Orbital objects.
        self._objects = list()
        # Stars.
        self._stars   = list()

        # Working image. Leave as None until ready to draw.
        self.workingImage = None

    ## Set orbit map image parameters.
    #  @param self            The object pointer.
    #  @param referenceHeight Hex map height in pixels.
    def _set_params(self, 
                    referenceHeight = None):
        # Check arguments
        self._referenceHeight = exception.arg_check(referenceHeight, int, self._height)

    ## Add asteroid belt to map in map group.
    def add_belt(self,
                 beltType):
        # Check arguments.
        exception.arg_check(beltType, str)

        # Add belt.
        # TODO: Set color
        self._objects.append(self.Belt(_ORBITAL_OBJECT_SIZE_RATIO_MAP[beltType],
                                       _ORBITAL_OBJECT_COLOR_MAP[beltType]))

    ## Add moon to last planet in map in map group.
    def add_moon(self,
                 moonType,
                 worldName=None):
        # Check arguments.
        exception.arg_check(moonType, str)
        exception.arg_check(worldName,   str)

        # Add station.
        # TODO: Set color
        sphereSatellites = self._objects[len(self._objects)-1].satellites
        sphereSatellites.append(self.Sphere(_ORBITAL_OBJECT_SIZE_RATIO_MAP[moonType],
                                            _ORBITAL_OBJECT_COLOR_MAP[moonType]))

    ## Add planet to map in map group.
    def add_planet(self,
                   planetType,
                   rings,
                   worldName=None):
        # Check arguments.
        exception.arg_check(planetType, str)
        exception.arg_check(rings,      bool)
        exception.arg_check(worldName,  str)

        # Add planet.
        # TODO: Set color
        self._objects.append(self.Sphere(_ORBITAL_OBJECT_SIZE_RATIO_MAP[planetType],
                                         _ORBITAL_OBJECT_COLOR_MAP[planetType],
                                         rings))

    ## Add star to system in map group.
    def add_star(self,
                 _color,
                 classification,
                 spectralSubclass,
                 luminosity,
                 solarMass,
                 solarRadius):
        # Check arguments.
        exception.arg_check(_color,           str)
        exception.arg_check(classification,   str)
        exception.arg_check(spectralSubclass, int)
        exception.arg_check(luminosity,       str)
        exception.arg_check(solarMass,        float)
        exception.arg_check(solarRadius,      float)

        # Classification string.
        classificationString = classification+str(spectralSubclass)+luminosity
        # Add star.
        self._stars.append(self.Star(_STAR_ORBIT_DIAMETER_RATIO*solarRadius,
                                     _STAR_COLOR_MAP[_color],
                                     classificationString))

    ## Add space station to last planet in map in map group.
    def add_station(self,
                    stationType,
                    worldName=None):
        # Check arguments.
        exception.arg_check(stationType, str)
        exception.arg_check(worldName,   str)

        # Add station.
        # TODO: Set color
        sphereSatellites = self._objects[len(self._objects)-1].satellites
        sphereSatellites.append(self.Station(_ORBITAL_OBJECT_SIZE_RATIO_MAP[stationType],
                                             _ORBITAL_OBJECT_COLOR_MAP[stationType]))

    ## Draw map image.
    def draw(self):
        # Blank image before drawing
        if not (self.workingImage is None):
            self.workingImage.close()

        # Initialize width and height.
        # Width is 0.
        # Height is reference height scaled by the number of stars.
        self.width  = 0
        self.height = self._referenceHeight
        xOffset = int(_ORBIT_X_OFFSET_RATIO*self._referenceHeight)
        yOffset = int(_ORBIT_Y_OFFSET_RATIO*self._referenceHeight)

        # Draw orbit map.
        # First pass, determine image size.
        # Second pass, draw image.
        for job in ['size','draw']:
            # Set new working image.
            if (job is 'draw'):
                self.workingImage = pilimage.new("RGBA", (self.width, self.height))
                drawingImage = pildraw.Draw(self.workingImage)
            # Initialize center y position.
            cY = self._referenceHeight/2
            # Initialize right of current object.
            right = 0
            # For each star. Draw largest to smallest
            starCountdown = len(self._stars)
            starCenterOffset = int(self._referenceHeight*_STAR_ORBIT_CENTER_OFFSET_RATIO)
            for s in sorted(self._stars, key=lambda r: r.sizeRatio, reverse=True):
                # Size of star.
                size = int(s.sizeRatio*self._referenceHeight)
                halfSize = size/2
                # Set right edge position for star.
                right = starCenterOffset*starCountdown
                # Set center x of star.
                cX = right - halfSize
                # Draw star.
                if (job is 'draw'):
                    # Create star image.
                    starShadow       = pilimage.new("RGBA", (self.width, self.height))
                    starShadowDrawingImage = pildraw.Draw(starShadow)
                    starForeground   = pilimage.new("RGBA", (self.width, self.height), s.color.rgba())
                    starBlurMask     = pilimage.new("L", (self.width, self.height), 0)
                    starDrawingImage = pildraw.Draw(starBlurMask)
                    # Draw star ellipse.
                    starDrawingImage.ellipse([(cX-halfSize, cY-halfSize),
                                              (cX+halfSize, cY+halfSize)],
                                             fill = 255)
                    starShadowDrawingImage.ellipse([(cX-halfSize, cY-halfSize),
                                                    (cX+halfSize, cY+halfSize)],
                                                   fill = color.GREY.rgba(50))
                    # Blur ellipse.
                    starBlurRadius = int(self._referenceHeight*_STAR_ORBIT_BLUR_RATIO)
                    starBlurMask = starBlurMask.filter(pilfilter.GaussianBlur(starBlurRadius))
                    # Paste ellipse.
                    self.workingImage = pilimage.alpha_composite(self.workingImage, starShadow)
                    self.workingImage = pilimage.composite(starForeground, self.workingImage, starBlurMask)
                    # Reset drawing image
                    drawingImage = pildraw.Draw(self.workingImage)
                # Decrement star count.
                starCountdown -= 1
            # Offset stars by more than planets
            right = starCenterOffset*len(self._stars) + xOffset
            # New width is max of right of stars or current width.
            if (job is 'size'):
                self.width = max(right, self.width)
            # For each orbital body.
            for o in self._objects:
                # Size of body.
                size = int(o.sizeRatio*self._referenceHeight)
                halfSize = size/2
                # Reinitialize center y position.
                cY = self._referenceHeight/2
                # Update left-most position for this body by adding offset.
                left = right + xOffset
                # Calculate new center
                cX = left + halfSize
                # Update right and bottom-most positions due to size.
                right  = left + size
                bottom = cY + halfSize
                # Update maximum width from the offset.
                if (job is 'size'):
                    self.width = max(right+xOffset, self.width)
                # For belts.
                if (type(o) is self.Belt):
                    if (job is 'draw'):
                        drawingImage.rectangle([(cX-halfSize, 0),
                                               (cX+halfSize,  self.height)],
                                              fill = o.color.rgba())
                # For other bodies.
                else:
                    # Draw body
                    if (job is 'draw'):
                        drawingImage.ellipse([(cX-halfSize, cY-halfSize),
                                              (cX+halfSize, cY+halfSize)],
                                             fill = o.color.rgba())
                    # Cycle through all satellites.
                    for s in o.satellites:
                        # Size of satellite.
                        size = int(s.sizeRatio*self._referenceHeight)
                        halfSize = size/2
                        # Update positions.
                        top    = bottom + yOffset
                        cY     = top + halfSize
                        bottom = top + size
                        # Update maximum height from the satellite size.
                        if (job is 'size'):
                            self.height = max(bottom+yOffset, self.height)
                        # Draw body
                        if (job is 'draw'):
                            # Draw stations.
                            if (type(s) is self.Station):
                                # Draw main truss.
                                drawingImage.rectangle([(cX-halfSize, cY-int(size*0.075)),
                                                        (cX+halfSize, cY+int(size*0.075))],
                                                       fill=s.color.rgba())
                                # Draw solar arrays.
                                drawingImage.rectangle([(cX-halfSize,                cY-halfSize),
                                                        (cX-halfSize+int(size*0.05), cY+halfSize)],
                                                       fill=s.color.rgba())
                                drawingImage.rectangle([(cX-halfSize+int(3*size*0.05),   cY-halfSize),
                                                        (cX-halfSize+int(4*size*0.05), cY+halfSize)],
                                                       fill=s.color.rgba())
                                drawingImage.rectangle([(cX+halfSize,                cY-halfSize),
                                                        (cX+halfSize-int(size*0.05), cY+halfSize)],
                                                       fill=s.color.rgba())
                                drawingImage.rectangle([(cX+halfSize-int(3*size*0.05),   cY-halfSize),
                                                        (cX+halfSize-int(4*size*0.05), cY+halfSize)],
                                                       fill=s.color.rgba())
                                # Draw module.
                                drawingImage.ellipse([(cX-int(halfSize*0.2), cY-int(halfSize*0.2)+int(size*0.15)),
                                                      (cX+int(halfSize*0.2), cY+int(halfSize*0.2)+int(size*0.15))],
                                                 fill = s.color.rgba())

                            # Draw spherical bodies.
                            else:
                                drawingImage.ellipse([(cX-halfSize, cY-halfSize),
                                                      (cX+halfSize, cY+halfSize)],
                                                     fill = s.color.rgba())

    ## Resize map image.
    def resize(self,
               referenceHeight):
        # Check arguments
        exception.arg_check(referenceHeight, int)

        # Set resized parameters.
        self._set_params(referenceHeight)

## Orbit map group class.
#
# The orbit map group class is used to create a group of images of 
# orbit maps. 
class OrbitMapGroup(object):
    ## Orbit map group class constructor.
    #  @param self             The object pointer.
    #  @param height           Image height in pixels.
    #  @param verticalMargin   Vertical margin.
    #  @param horizontalMargin Horizontal margin.
    def __init__(self,
                 height,
                 verticalMargin,
                 horizontalMargin):
        # Check arguments.
        # Image height.
        self._height = exception.arg_check(height, int)
        # Image margin.
        self._verticalMargin   = exception.arg_check(verticalMargin,   int)
        self._horizontalMargin = exception.arg_check(horizontalMargin, int)

        # Maps
        self.maps = dict()

        # Working image. Leave as None until ready to draw.
        self.workingImage = None

    ## Set orbit map group image parameters.
    #  @param self             The object pointer.
    #  @param height           Hex map height in pixels.
    #  @param verticalMargin   Top margin in pixels.
    #  @param horizontalMargin Bottom margin in pixels.
    def _set_params(self, 
                    height           = None,
                    verticalMargin   = None,
                    horizontalMargin = None):
        # Check arguments
        self._height           = exception.arg_check(height,           int, self._height)
        self._verticalMargin   = exception.arg_check(verticalMargin,   int, self._verticalMargin)
        self._horizontalMargin = exception.arg_check(horizontalMargin, int, self._horizontalMargin)

    ## Add system to map group.
    def add_system(self,
                   majorRow,
                   majorCol,
                   hRow, 
                   hCol,
                   systemName):
        # Check arguments.
        exception.arg_check(majorRow,       int)
        exception.arg_range_check(majorRow, 0, 9)
        exception.arg_check(majorCol,       int)
        exception.arg_range_check(majorCol, 0, 9)
        exception.arg_check(hRow,           int)
        exception.arg_range_check(hRow,     0, 9)
        exception.arg_check(hCol,           int)
        exception.arg_range_check(hCol,     0, 9)
        exception.arg_check(systemName,     str)

        # Check to see if system exists.
        hexKey = (hRow, hCol)
        if (self.system_exists(hRow, hCol)):
            raise exception.ExistingDictKey(hexKey)
        else:
            self.maps[hexKey] = OrbitMap(systemName, 
                                         int(self._height*_SYSTEM_MAP_HEIGHT_RATIO))

    ## Draw map group.
    #  @param self The object pointer.
    def draw(self):
        # Blank image before drawing
        if not (self.workingImage is None):
            self.workingImage.close()

        # Draw maps
        for mKey in self.maps.iterkeys():
            self.maps[mKey].draw()

        # New working image.
        #self.workingImage = pilimage.new("RGBA", (self._size,self._size))

    ## Reset hex.
    #  @param self The object pointer.
    def reset_hex(self,
                  hRow, 
                  hCol):
        # Check arguments.
        exception.arg_check(hRow,           int)
        exception.arg_range_check(hRow,     0, 9)
        exception.arg_check(hCol,           int)
        exception.arg_range_check(hCol,     0, 9)

        # Delete hex
        hexKey = (hRow, hCol)
        if (self.maps.has_key(hexKey)):
            del self.maps[hexKey]

    ## Save orbit map group.
    def save(self, path):
        # Check arguments.
        path = exception.arg_check(path, str)

        # Draw image if it hasn't been
        if self.workingImage is None:
            self.draw()

        ## DEBUG
        # 10 has station
        # 2 has station
        saveMap = self.maps[self.maps.keys()[25]]
        saveImage = saveMap.workingImage.resize((saveMap.width/_SECTOR_IMAGE_SCALE,
                                                 saveMap.height/_SECTOR_IMAGE_SCALE),
                                                pilimage.HAMMING)

        # Save image
        saveImage.save(path)

    ## Check to see if system exists.
    def system_exists(self,
                      hRow, 
                      hCol):
        # Check arguments.
        exception.arg_check(hRow,       int)
        exception.arg_range_check(hRow, 0, 9)
        exception.arg_check(hCol,       int)
        exception.arg_range_check(hCol, 0, 9)
        # Check to see if system exists.
        hexKey = (hRow, hCol)
        if (self.maps.has_key(hexKey)):
            return True
        else:
            return False


## Sector image class.
#
#  The sector image class is used to create images of an SWN sector.
class SectorImage(object):
    ## Sector image class constructor.
    #  @param self                  The object pointer.
    #  @param sectorName            Name of sector.
    #  @param majorRow              Major row of sector.
    #  @param majorCol              Major column of sector.
    #  @param rows                  Number of hex rows (odd-q).
    #  @param cols                  Number of hex columns (odd-q).
    #  @param width                 Image width in pixels.
    #  @param verticalMarginRatio   Vertical margin ratio relative to width.
    #  @param horizontalMarginRatio Horizontal margin ratio relative to width.
    #  @param gridColor             Color of gridlines.
    def __init__(self,
                 sectorName,
                 majorRow,
                 majorCol,
                 rows,
                 cols,
                 width                 = None,
                 verticalMarginRatio   = None,
                 horizontalMarginRatio = None,
                 gridColor         = _GRID_COLOR):
        # Check arguments
        self._sectorName            = exception.arg_check(sectorName,            str)
        self._majorRow              = exception.arg_check(majorRow,              int)
        self._majorCol              = exception.arg_check(majorRow,              int)
        self._rows                  = exception.arg_check(rows,                  int)
        self._cols                  = exception.arg_check(cols,                  int)
        self._width                 = exception.arg_check(width,                 int,         _SECTOR_IMAGE_WIDTH*_SECTOR_IMAGE_SCALE)
        self._verticalMarginRatio   = exception.arg_check(verticalMarginRatio,   float,       _SECTOR_VERTICAL_MARGIN_RATIO)
        self._horizontalMarginRatio = exception.arg_check(horizontalMarginRatio, float,       _SECTOR_HORIZONTAL_MARGIN_RATIO)
        self._gridColor             = exception.arg_check(gridColor,             color.Color, _GRID_COLOR)

        # Set sector map size
        self._set_params(width, 
                         self._verticalMarginRatio, 
                         self._horizontalMarginRatio)

        # Load background starfield image
        # Darken background image
        self._background = pilenhance.Brightness(pilimage.open(_IMAGE_BACKGROUND).convert('RGBA')).enhance(_IMAGE_BACKGROUND_BRIGHTNESS)

        # Create hex map.
        self.hexMap = HexMap(self._majorRow, 
                             self._majorCol, 
                             self._rows, 
                             self._cols, 
                             self._width, 
                             self._height, 
                             self._hexSize, 
                             self._horizontalMargin, 
                             self._verticalMargin,
                             self._gridColor,
                             self._background)
        # Create info table.
        self.infoTable = InfoTable(self._sectorName, 
                                   self._height, 
                                   self._verticalMargin,
                                   self._horizontalMargin,
                                   self._background)
        # Create orbit maps.
        self.orbitMapGroup = OrbitMapGroup(self._height, 
                                           self._verticalMargin,
                                           self._horizontalMargin)

        # Create ancillary sector info images
        #self.corporations
        #self.religions

    ## Internally set image parameters.
    #
    #  @param self                  The object pointer.
    #  @param width                 Image width in pixels.
    #  @param verticalMarginRatio   Vertical margin ratio relative to height.
    #  @param horizontalMarginRatio Horizontal margin ratio relative to height.
    #  @param gridColor             Color of gridlines.
    def _set_params(self,
                    width                 = None,
                    verticalMarginRatio   = None,
                    horizontalMarginRatio = None,
                    gridColor             = None):
        # Check arguments
        width                 = exception.arg_check(width,                 int,         self._width)
        verticalarginRatio    = exception.arg_check(verticalMarginRatio,   float,       self._verticalMarginRatio)
        horizontalMarginRatio = exception.arg_check(horizontalMarginRatio, float,       self._horizontalMarginRatio)
        gridColor             = exception.arg_check(gridColor,             color.Color, self._gridColor)

        # Grid information
        rows = self._rows
        cols = self._cols

        # Margins in pixels
        verticalMargin   = int(width*verticalMarginRatio)
        horizontalMargin = int(width*horizontalMarginRatio)

        # Map width
        mapWidth = width - 2*horizontalMargin

        # Hex sizes
        hexSizeByWidth = float(2.0*mapWidth)/float(3.0*cols+1.0)
        hexSize        = hexSizeByWidth
        hexWidth       = float(hexSize*2.0)
        hexHeight      = float(float(math.sqrt(3.0)/2.0)*float(hexWidth))

        # Map height
        mapHeight = int((math.sqrt(3.0)/2.0)*hexSize*(2.0*rows+1))

        # Height
        height = int(mapHeight + 2*verticalMargin)

        # Map bounding box        
        mapTopLeft     = (horizontalMargin,          verticalMargin)
        mapTopRight    = (horizontalMargin+mapWidth, verticalMargin)
        mapBottomRight = (horizontalMargin+mapWidth, verticalMargin+mapHeight)
        mapBottomLeft  = (horizontalMargin,          verticalMargin+mapHeight)

        # Drawing specifications
        routeWidth       = int(hexSize*_ROUTE_WIDTH_RATIO)
        routeBlurSize    = routeWidth*_ROUTE_BLUR_SIZE_RATIO
        gridWidth        = int(routeWidth*_GRID_WIDTH_RATIO)
           
        
        # Store values
        self._size             = (width, height)
        self._width            = width
        self._height           = height
        self._verticalMargin   = verticalMargin
        self._horizontalMargin = horizontalMargin
        self._hexSize          = hexSize
        self._routeWidth       = routeWidth
        self._routeBlurSize    = routeBlurSize
        self._gridWidth        = gridWidth

    def draw_sector(self):
        # Draw layers ----------------------------------------------------------
        self.hexMap.draw()
        self.infoTable.draw()
        self.orbitMapGroup.draw()

        # Determine width

        # Combine layers -------------------------------------------------------

    ## Resize images.
    #  @param self                  The object pointer.
    #  @param width                 Image width in pixels.
    #  @param verticalMarginRatio   Vertical margin ratio relative to height.
    #  @param horizontalMarginRatio Horizontal margin ratio relative to height.
    def resize(self,
               width                 = None,
               verticalMarginRatio   = None,
               horizontalMarginRatio = None):
        # Check arguments
        width                 = exception.arg_check(width,             int,   _SECTOR_IMAGE_WIDTH)
        verticalMarginRatio   = exception.arg_check(topMarginRatio,    float, _SECTOR_VERTICAL_MARGIN_RATIO)
        horizontalMarginRatio = exception.arg_check(bottomMarginRatio, float, _SECTOR_HORIZONTAL_MARGIN_RATIO)

        # Set sector map size
        self._set_params(width, verticalMarginRatio, horizontalMarginRatio)
        width            = self._size[0]
        height           = self._size[1]
        hexSize          = self._hexSize
        gridWidth        = self._gridWidth
        verticalMargin   = self._verticalMargin
        horizontalMargin = self._horizontalMargin

        # Resize sector main images
        self.hexMap.resize(hexSize)
        self.infoTable.resize(height)
        self.orbitMapGroup.resize()

    ## Save sector hex map.
    def save_sector_map(self, path):
        # Check arguments.
        path = exception.arg_check(path, str)
        # Save hexmap.
        self.hexMap.save(path)

    ## Save sector info table.
    def save_sector_info(self, path):
        # Check arguments.
        path = exception.arg_check(path, str)
        # Save hexmap.
        self.infoTable.save(path)

    ## Save sector orbit maps.
    def save_sector_orbits(self, path):
        # Check arguments.
        path = exception.arg_check(path, str)
        # Save map group.
        self.orbitMapGroup.save(path)

    ## Save combined sector hex map, info table, and orbit maps.
    def save_sector_combined(self):
        raise Exception('Not implemented yet.')

    ## Externally set image parameters.
    #
    #  @param self                  The object pointer.
    #  @param width                 Image width in pixels.
    #  @param verticalMarginRatio   Vertical margin ratio relative to height.
    #  @param horizontalMarginRatio Horizontal margin ratio relative to height.
    #  @param gridColor             Color of gridlines.
    def set_params(self,
                   width                 = None,
                   verticalMarginRatio   = None,
                   horizontalMarginRatio = None,
                   gridColor             = None):
        # Check arguments
        width                 = exception.arg_check(width,                 int,         self._width)
        verticalMarginRatio   = exception.arg_check(verticalMarginRatio,   float,       self._verticalMarginRatio)
        horizontalMarginRatio = exception.arg_check(horizontalMarginRatio, float,       self._horizontalMarginRatio)
        gridColor             = exception.arg_check(gridColor,             color.Color, self._gridColor)
        # Set internal parameters.
        _set_params(width,
                    verticalMarginRatio,
                    horizontalMarginRatio,
                    gridColor)
        # Set hex map parameters
        # Set info table parameters
        # Set orbit map parameters