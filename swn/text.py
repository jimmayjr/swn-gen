#!/usr/bin/env python

import math

import exception
import hexutils
import sector

# HexMap constants -------------------------------------------------------------
# Map border
MAP_BORDER = '#'

# Map sizes
LARGE_MAP = 'large'
SMALL_MAP = 'small'

# Plaintext hex representations
#   HEIGHT AND WIDTH MUST BE ODD
LARGE_ODDR_TEXT = [r'   _______    ',
                   r'  /       \   ',
                   r' /         \  ',
                   r'/           \ ',
                   r'\           / ',
                   r' \         /  ',
                   r'  \_______/   ']
LARGE_ODDR_TEXT_W =     13    # Width
LARGE_ODDR_TEXT_H =     7     # Height
LARGE_ODDR_TEXT_COORD = (1,4) # Coordinate position, zero indexed
LARGE_ODDR_TEXT_LABEL = (4,6) # Label position, zero indexed 

SMALL_ODDR_TEXT = [r'  _____   ',
                   r' /     \  ',
                   r'/       \ ',
                   r'\       / ',
                   r' \_____/  ']
SMALL_ODDR_TEXT_W =     9     # Width
SMALL_ODDR_TEXT_H =     5     # Height
SMALL_ODDR_TEXT_COORD = (1,2) # Coordinate position, zero indexed
SMALL_ODDR_TEXT_LABEL = (3,4) # Label position, zero indexed 

# Orbit map constants ----------------------------------------------------------
ORBIT_SATELLITE_SYMBOL = ':-'
ORBIT_SEPARATOR        = '|'

# Table constants --------------------------------------------------------------
# Column justification
JUSTIFY_CENTER = 'C'
JUSTIFY_LEFT   = 'L'
JUSTIFY_RIGHT  = 'R'
# Separators and borders
TABLE_BORDER  = '#'
TABLE_COL_SEP = '|'
TABLE_ROW_SEP = '-'

class HexMap(object):
    def __init__(self,
                 title  = None,
                 size   = None,
                 rows   = None,
                 cols   = None,
                 coords = None,
                 border = None):
        # Argument parsing -----------------------------------------------------
        # Map title
        self.title = exception.arg_check(title,str,'')
        # Map size
        if ( not ( (size == LARGE_MAP ) or ( size == SMALL_MAP ) ) ):
            # TODO: raise error of invalid map size argument
            size = SMALL_MAP
        self.size  = exception.arg_check(size,str,SMALL_MAP)
        # Hex text info
        if ( self.size == LARGE_MAP ):
            hexText        = LARGE_ODDR_TEXT
            self.hexWidth  = LARGE_ODDR_TEXT_W
            self.hexHeight = LARGE_ODDR_TEXT_H
            hexCoord       = LARGE_ODDR_TEXT_COORD
            self.hexLabel  = LARGE_ODDR_TEXT_LABEL
        else:
            hexText        = SMALL_ODDR_TEXT
            self.hexWidth  = SMALL_ODDR_TEXT_W
            self.hexHeight = SMALL_ODDR_TEXT_H
            hexCoord       = SMALL_ODDR_TEXT_COORD
            self.hexLabel  = SMALL_ODDR_TEXT_LABEL
        # Map rows
        self.rows = exception.arg_check(rows,int,sector.SECTOR_ROWS)
        # Map columns
        self.cols = exception.arg_check(cols,int,sector.SECTOR_COLS)
        # Print map coordinates flag
        coords = exception.arg_check(coords,bool,False)
        # Map border
        self.border = exception.arg_check(border,str,MAP_BORDER)
        # Map padding
        self.padding = 1

        # Create empty grid from template --------------------------------------
        # Calculate number of rows
        charRows  = self.rows*self.hexHeight + int(math.ceil((self.hexHeight-1)/2.0))
        # Subtract the rows where the grid overlaps
        charRows -= (self.rows - 1)
        # Calculate number of columns
        #   Add full width of 0th column
        charCols  = self.hexWidth
        #   Every extra column is 3/4 of the width to the right 
        charCols += (self.cols-1)*int(math.ceil(self.hexWidth*3.0/4.0))
        # Fill hexmap
        self.hexMap = [ ([' '] * charCols) for i in xrange(charRows) ]
        # Array character row offset to start this hex from
        cEvenColRowOffset = 0
        cOddColRowOffset = (self.hexHeight-1)/2
        # For every hex row
        for row in xrange(self.rows):
            # Array character column offset to start this hex from
            cColOffset = 0
            # For every hex col
            for col in xrange(self.cols):
                # Rows to copy from template
                tRows = xrange(self.hexHeight)
                # Cols to copy from template
                tCols = xrange(self.hexWidth)
                # Copy template
                for tr in tRows:
                    for tc in tCols:
                        # Use different row offsets for even vs odd rows
                        useOffset = cEvenColRowOffset
                        if (col % 2 != 0):
                            useOffset = cOddColRowOffset
                        # Don't copy spaces
                        if (hexText[tRows[tr]][tCols[tc]] != ' '):
                            self.hexMap[useOffset+tr][cColOffset+tc] = hexText[tRows[tr]][tCols[tc]]
                # Add hex coords
                if (coords):
                    coordStr = '0{0}0{1}'.format(row,col)
                    coordROffset = hexCoord[0]
                    coordCOffset = hexCoord[1]
                    for i in xrange(len(coordStr)):
                        self.hexMap[useOffset+coordROffset][cColOffset+coordCOffset+i] = coordStr[i]

                # Update character column offset
                cColOffset += int(math.ceil(self.hexWidth*3.0/4.0))
            # Update character row offset
            cEvenColRowOffset += self.hexHeight-1
            cOddColRowOffset  += self.hexHeight-1

    def add_label(self,
                 label,
                 row,
                 col):
        # Check arguments
        exception.arg_check(label,str)
        exception.arg_check(row,int)
        exception.arg_check(col,int)
        # Array character row offset to start this hex from
        cRowOffset = row*(self.hexHeight-1)
        # Offset more for odd columns
        if (col % 2 != 0):
            cRowOffset += (self.hexHeight-1)/2
        # Array character column offset
        cColOffset = col*int(math.ceil(self.hexWidth*3.0/4.0))
        # Offset to center of hex
        cRowOffset += self.hexLabel[0]
        cColOffset += self.hexLabel[1]
        # Print 
        for i in xrange(len(label)):
            self.hexMap[cRowOffset][cColOffset+i] = label[i]

    def print_text(self):
        mapWidth  = len(self.hexMap[0])
        border  = self.border*(mapWidth + self.padding*2 + 2)
        padding = self.border + ' '*(self.padding*2 + mapWidth) + self.border
        # Print top border
        print(border)
        # Print title
        print(self.border + ' ' + self.title.ljust(mapWidth) + ' ' + self.border)
        # Print title separator
        print(border)
        # Print map
        for r in self.hexMap:
            print(self.border + ' ' + ''.join(r) + ' ' + self.border)
        # Print bottom border
        print(padding)
        print(border)

class OrbitMap(object):
    def __init__(self,
                 title  = None,
                 border = None):
        # Map title
        self.title = exception.arg_check(title,str,'')
        # Map border
        self.border = exception.arg_check(border,str,MAP_BORDER)
        # Map padding
        self.mapPadding = 1
        # Orbit padding
        self.orbitPadding = 2
        # Map orbits
        self.orbits = list()

    def add_orbit(self,
                  bodies     = None,
                  satellites = None):
        # Check arguments
        bodies = exception.arg_check(bodies,list,list())
        satellites = exception.arg_check(satellites,list,list())
        for b in bodies:
            exception.arg_check(b,str)
        for s in satellites:
            exception.arg_check(s,str)
        # Create list for orbit
        orbit = list()
        # Add bodies to orbit
        for b in bodies:
            orbit.append(b)
        # Add satellites to orbit
        for s in satellites:
            orbit.append(ORBIT_SATELLITE_SYMBOL + s)
        # Add orbit to map list
        self.orbits.append(orbit)

    def print_text(self):
        # Determine number of rows to create based on the largest number of 
        # bodies in an orbit
        rows = [''] * max(map(lambda orbit: len(orbit), self.orbits))
        # Add border and padding to rows at beginning
        for rIndex in xrange(len(rows)):
            rows[rIndex] += self.border + ' '*self.mapPadding
        # Add orbits to rows
        orbitCount = 0
        orbitMax = len(self.orbits)
        for orbit in self.orbits:
            # Number of columns should be the longest orbit text
            numCols = max(map(lambda objectString: len(objectString), orbit))
            # Get text for new columns of rows
            newCols = [' '*numCols]*len(rows)
            for bodyIndex in xrange(len(orbit)):
                bodyString = orbit[bodyIndex]
                newCols[bodyIndex] = bodyString + newCols[bodyIndex][len(bodyString):]
            # Add orbit text to rows
            for rIndex in xrange(len(rows)):
                rows[rIndex] += newCols[rIndex]
            orbitCount += 1
            # Add orbit separator
            if ( orbitCount != orbitMax ):
                for rIndex in xrange(len(rows)):
                    rows[rIndex] += ' '*self.orbitPadding + ORBIT_SEPARATOR + ' '*self.orbitPadding
        # Add border and padding to rows at end
        for rIndex in xrange(len(rows)):
            rows[rIndex] += ' '*self.mapPadding + self.border

        # Print heading
        mapWidth = len(rows[0])
        print(self.border*mapWidth)
        print(self.border + ' ' + self.title + ' '*(mapWidth-len(self.title)-3) + self.border)
        print(self.border*mapWidth)
        # Print rows
        for r in rows:
            print(r)
        # Print end
        print(self.border*mapWidth)
        # Print empty line
        print('')

class Table(object):
    def __init__(self,title=None,border=None,colSep=None,rowSep=None):
        # Table title
        self.title = exception.arg_check(title,str,'')
        # Table border character
        self.border = exception.arg_check(border,str,TABLE_BORDER)
        # Table column separator character
        self.colSep = exception.arg_check(colSep,str,TABLE_COL_SEP)
        # Table row separator character
        self.rowSep = exception.arg_check(rowSep,str,TABLE_ROW_SEP)
        # Column Headings
        self.headings = list()
        # Column justification
        self.justify = list()
        # Data rows
        self.rows = list()

    def add_heading(self,heading=None,justify=None):
        # If argument is a single value make it a list with one entry
        if ( type(heading) is not list ):
            heading = [heading]
        # Add each heading in list
        for h in heading:
            # Add heading
            self.headings.append(exception.arg_check(h,str,''))
            # Set column justification
            j = exception.arg_check(justify,str,'L')
            if ( (j != JUSTIFY_LEFT.lower()) or (j != JUSTIFY_CENTER.lower()) or (j != JUSTIFY_RIGHT.lower()) or
                 (j != JUSTIFY_LEFT)         or (j != JUSTIFY_CENTER)         or (j != JUSTIFY_RIGHT) ):
                self.justify.append(j.upper())
            else:
                # TODO, raise unknown justification error
                self.justify.append(JUSTIFY_LEFT)
            # Append empty data to end of rows if they exist already
            for r in self.rows:
                r.append('')

    def add_row(self,row=None):
        # Check that row is a list
        row  = exception.arg_check(row,list,list())
        # Add empty data if row data does not have enough columns
        row += ['' for diff in xrange(len(self.headings)-len(row))]
        # Add to rows list
        self.rows.append(row)

    def print_text(self):
        # Calculate maximum width of each column
        colWidth = dict()
        # Start with base value being the width of the headings
        for h in self.headings:
            colWidth[h] = len(h)+2
        # Look at each row and compare the width of each column to the current max
        for r in self.rows:
            for cIndex in xrange(len(r)):
                # Get heading for this row
                h = self.headings[cIndex]
                # Use max of this column length vs the current max
                colWidth[h] = max(len(str(r[cIndex]))+2,colWidth[h])
        # Calculate table width
        #    Sum of column max widths + # of column separators + border on each side
        tableWidth = sum(colWidth.values()) + len(self.headings)-1 + 2
        # Print title if it has one
        if ( len(self.title) > 0 ):
            print(self.border*tableWidth)
            print(self.border + ' ' + self.title + ' '*(tableWidth-len(self.title)-3) + self.border)
            print(self.border*tableWidth)
        # Print headings
        line = self.border
        for hIndex in xrange(len(self.headings)-1):
            line += (' ' + self.headings[hIndex] + ' ').ljust(colWidth[self.headings[hIndex]]) + self.colSep
        line += (' ' + self.headings[hIndex+1]).ljust(colWidth[self.headings[hIndex+1]]) + self.border
        print(line)
        # Print heading separator
        print(self.border + self.rowSep*(tableWidth-2) + self.border)
        # Print rows
        for r in self.rows:
            line = self.border
            for cIndex in xrange(len(r)-1):
                colText = (' ' + r[cIndex] + ' ')
                if ( self.justify[cIndex] == JUSTIFY_RIGHT ):
                    line += colText.rjust(colWidth[self.headings[cIndex]])
                elif ( self.justify[cIndex] == JUSTIFY_CENTER ):
                    line += colText.cjust(colWidth[self.headings[cIndex]])
                else:
                    line += colText.ljust(colWidth[self.headings[cIndex]])
                line += self.colSep
            # Last column doesn't have separator
            colText = (' ' + r[cIndex+1] + ' ')
            if ( self.justify[cIndex+1] == JUSTIFY_RIGHT ):
                line += colText.rjust(colWidth[self.headings[cIndex+1]])
            elif ( self.justify[cIndex+1] == JUSTIFY_CENTER ):
                line += colText.cjust(colWidth[self.headings[cIndex+1]])
            else:
                line += colText.ljust(colWidth[self.headings[cIndex+1]])
            line += self.border
            print(line)
        # Print end
        print(self.border*tableWidth)