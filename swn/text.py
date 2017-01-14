#!/usr/bin/env python

import exception

TABLE_BORDER  = '#'
TABLE_COL_SEP = '|'
TABLE_ROW_SEP = '-'

JUSTIFY_CENTER = 'C'
JUSTIFY_LEFT   = 'L'
JUSTIFY_RIGHT  = 'R'

class Table(object):
    def __init__(self,title=None,border=None,colSep=None,rowSep=None):
        # Table title
        self.title = exception.ArgCheck(title,str,'')
        # Table border character
        self.border = exception.ArgCheck(border,str,TABLE_BORDER)
        # Table column separator character
        self.colSep = exception.ArgCheck(colSep,str,TABLE_COL_SEP)
        # Table row separator character
        self.rowSep = exception.ArgCheck(rowSep,str,TABLE_ROW_SEP)
        # Column Headings
        self.headings = list()
        # Column justification
        self.justify = list()
        # Data rows
        self.rows = list()

    def AddHeading(self,heading=None,justify=None):
        # If argument is a single value make it a list with one entry
        if ( type(heading) is not list ):
            heading = [heading]
        # Add each heading in list
        for h in heading:
            # Add heading
            self.headings.append(exception.ArgCheck(h,str,''))
            # Set column justification
            j = exception.ArgCheck(justify,str,'L')
            if ( (j != JUSTIFY_LEFT.lower()) or (j != JUSTIFY_CENTER.lower()) or (j != JUSTIFY_RIGHT.lower()) or
                 (j != JUSTIFY_LEFT)         or (j != JUSTIFY_CENTER)         or (j != JUSTIFY_RIGHT) ):
                self.justify.append(j.upper())
            else:
                # TODO, raise unknown justification error
                self.justify.append(JUSTIFY_LEFT)
            # Append empty data to end of rows if they exist already
            for r in self.rows:
                r.append('')

    def AddRow(self,row=None):
        # Check that row is a list
        row  = exception.ArgCheck(row,list,list())
        # Add empty data if row data does not have enough columns
        row += ['' for diff in xrange(len(self.headings)-len(row))]
        # Add to rows list
        self.rows.append(row)

    def Print(self):
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