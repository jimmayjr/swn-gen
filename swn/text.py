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
            colWidth[h] = len(h)
        # Look at each row and compare the width of each column to the current max
        for r in self.rows:
            for cIndex in xrange(len(r)):
                # Get heading for this row
                h = self.headings[cIndex]
                # Use max of this column length vs the current max
                colWidth[h] = max(len(str(r[cIndex])),colWidth[h])
        # Calculate table width
        #    Sum of column max widths + space pad on each side of columns + border on each side
        tableWidth = sum(colWidth.values()) + 2*len(self.headings) + 2
        # Print title if it has one
        if ( len(self.title) > 0 ):
            print(self.border*tableWidth)
            print(self.border + ' ' + self.title + ' '*(len(tableWidth)-len(self.title)+1) + self.border)
            print(self.border*tableWidth)