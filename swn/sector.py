#!/usr/bin/env python

from __future__ import print_function

import math
import numpy as np
import operator

import exception
import generator
import hexutils
import system
import text

MAX_ROWS = 10
MAX_COLS = 8

# Sector class -----------------------------------------------------------------
class Sector(object):
    def __init__(self,
                 name):
        # General information
        self.name = exception.ArgCheck(name,str,argDefault='Default Name')
        # Roll information
        self.corporations = list()
        self.heresies = list()
        self.parties = list()
        self.religions = list()
        self.systems = dict()

    def addBlankSystem(self,sName,sRow,sCol):
        if (not self.hexEmpty(sRow,sCol)):
            raise exception.ExistingDictKey((sRow,sCol))
        else:
            self.systems[(sRow,sCol)] = system.System(name = sName,
                                                      stars = list(),
                                                      objects = list(),
                                                      worlds = list())

    def hexEmpty(self,sRow,sCol):
        return(not self.systems.has_key((sRow,sCol)))

    def printCorporations(self):
        # Create table
        table = text.Table(self.name + ' - ' + 'Sector Corporations')
        # Add headings
        table.AddHeading('Index')
        table.AddHeading('Corporation')
        table.AddHeading('Business')
        # Add rows
        cIndex = 1
        for c in self.corporations:
            # Initialize row list
            row = list()
            # Append index
            row.append(str(cIndex).rjust(2))
            # Append name
            row.append(c.name + ' ' + c.organization)
            # Append business type
            row.append(c.business)
            # Append row
            table.AddRow(row)
            # Update corporation index
            cIndex += 1
        # Print table
        table.Print()

    def printReligions(self):
        # Create table
        table = text.Table(self.name + ' - ' + 'Sector Religions')
        # Add headings
        table.AddHeading('Index')
        table.AddHeading('Evolution')
        table.AddHeading('Leadership')
        table.AddHeading('Origin Tradition')
        # Add rows
        rIndex = 1
        for r in self.religions:
            # Initialize row
            row = list()
            # Append index
            row.append(str(rIndex).rjust(2))
            # Append evolution
            row.append(r.evolution)
            # Append leadership
            row.append(r.leadership)
            # Append origin
            row.append(r.origin)
            # Add row
            table.AddRow(row)
            # Update index
            rIndex += 1
        # Print table
        table.Print()

    def PrintSectorInfo(self):
        # Create table
        table = text.Table(self.name + ' - ' + 'Sector Info')
        # Add headings
        table.AddHeading('Index')
        table.AddHeading('Hex')
        table.AddHeading('System')
        table.AddHeading('World')
        table.AddHeading('Atmosphere')
        table.AddHeading('Biosphere')
        table.AddHeading('Population')
        table.AddHeading('Pop. Alt.','R')
        table.AddHeading('Tags')
        table.AddHeading('Temperature')
        table.AddHeading('TL')
        # Add rows
        wIndex = 1
        for systemKey in self.SortedSystems():
            system = self.systems[systemKey]
            # Keep track of first world in system so we only print the index,
            # hex, and system name for the first entry
            firstWorld = True
            for w in system.SortedWorlds():
                row = list()
                # Index
                row.append(str(wIndex).rjust(2))
                # Print hex and system name for first world in system
                if ( firstWorld ):
                    firstWorld = False
                    # Hex
                    row.append('0{0}0{1}'.format(systemKey[0],systemKey[1]))
                    # System name
                    row.append(system.name)
                else:
                    # Hex
                    row.append('')
                    # System name
                    row.append('')
                # World name
                row.append(w.name)
                # Atmosphere
                row.append(w.atmosphere)
                # Biosphere
                row.append(w.biosphere)
                # Population
                row.append(w.population)
                # Population alt.
                row.append(w.PopulationAltText())
                # Tags
                row.append(w.tags[0] + ', ' + w.tags[1])
                # Temperature
                row.append(w.temperature)
                # TL
                row.append(w.techLevel)
                # Add row
                table.AddRow(row)
                # Update world index
                wIndex += 1
        # Print table
        table.Print()

    def printSectorMap(self,
                       coords = True,
                       stars  = True):
        # Create hexmap as empty list of lists of characters -------------------
        #   Each row is a list
        #   Each column is an entry in the row list
        # Calculate number of rows
        charRows  = MAX_ROWS*hexutils.ODDR_TEXT_H + int(math.ceil((hexutils.ODDR_TEXT_H-1)/2.0))
        # Subtract the rows where the grid overlaps
        charRows -= (MAX_ROWS - 1)
        # Calculate number of columns
        #   Add full width of 0th column
        charCols  = hexutils.ODDR_TEXT_W
        #   Every extra column is 3/4 of the width to the right 
        charCols += (MAX_COLS-1)*int(math.ceil(hexutils.ODDR_TEXT_W*3.0/4.0))
        # Subtract columns where the grid overlaps
        # Fill hexmap
        hexMap = [ ([' '] * charCols) for i in xrange(charRows) ]
        # Add grid from template -----------------------------------------------
        # Array character row offset to start this hex from
        cEvenColRowOffset = 0
        cOddColRowOffset = (hexutils.ODDR_TEXT_H-1)/2
        # For every hex row
        for row in xrange(MAX_ROWS):
            # Array character column offset to start this hex from
            cColOffset = 0
            # For every hex col
            for col in xrange(MAX_COLS):
                # Rows to copy from template
                tRows = xrange(hexutils.ODDR_TEXT_H)
                # Cols to copy from template
                tCols = xrange(hexutils.ODDR_TEXT_W)
                # Copy template
                for tr in xrange(len(tRows)):
                    for tc in xrange(len(tCols)):
                        # Use different row offsets for even vs odd rows
                        useOffset = cEvenColRowOffset
                        if (col % 2 != 0):
                            useOffset = cOddColRowOffset
                        # Don't copy spaces
                        if (hexutils.ODDR_TEXT[tRows[tr]][tCols[tc]] != ' '):
                            hexMap[useOffset+tr][cColOffset+tc] = hexutils.ODDR_TEXT[tRows[tr]][tCols[tc]]
                # Add hex coords
                if (coords):
                    coordStr = '0{0}0{1}'.format(row,col)
                    coordROffset = hexutils.ODDR_TEXT_COORD[0]
                    coordCOffset = hexutils.ODDR_TEXT_COORD[1]
                    for i in xrange(len(coordStr)):
                        hexMap[useOffset+coordROffset][cColOffset+coordCOffset+i] = coordStr[i]

                # Update character column offset
                cColOffset += int(math.ceil(hexutils.ODDR_TEXT_W*3.0/4.0))
            # Update character row offset
            cEvenColRowOffset += hexutils.ODDR_TEXT_H-1
            cOddColRowOffset  += hexutils.ODDR_TEXT_H-1
        # Add star systems------------------------------------------------------
        if (stars):
            # Sort star systems by hex, col first, row second
            starKeys = self.SortedSystems()
            for starKeyIndex in range(len(starKeys)):
                # Get row and column
                (row,col) = starKeys[starKeyIndex]
                # Array character row offset to start this hex from
                cRowOffset = row*(hexutils.ODDR_TEXT_H-1)
                # Offset more for odd columns
                if (col % 2 != 0):
                    cRowOffset += (hexutils.ODDR_TEXT_H-1)/2
                # Array character column offset
                cColOffset = col*int(math.ceil(hexutils.ODDR_TEXT_W*3.0/4.0))
                # Offset to center of hex
                cRowOffset += hexutils.ODDR_TEXT_LABEL[0]
                cColOffset += hexutils.ODDR_TEXT_LABEL[1]
                # Print 
                starNum = str(starKeyIndex)
                for i in xrange(len(starNum)):
                    hexMap[cRowOffset][cColOffset+i] = starNum[i]

        # Print characters to screen -------------------------------------------
        # Print top border
        border = ''
        for i in xrange(len(hexMap[0])+4):
            border += '#'
        print(border)
        # Print sector name
        sectorLine = border
        sectorText = ' ' + self.name + ' - ' + 'Sector Map' + ' '
        sectorLine = sectorLine[:1] + sectorText + sectorLine [(1+len(sectorText)):]
        print(sectorLine)
        print(border)
        # Print map
        for rowList in hexMap:
            line = '# '
            for colChar in rowList:
                line += colChar
            line += ' #'
            print(line)
        # Print bottom border
        line = '#'
        for i in xrange(1,len(hexMap[0])+3):
            line += ' '
        line += '#'
        print(line)
        print(border)

    def SortedSystems(self):
        return(sorted(self.systems.iterkeys(),key=lambda e: (e[1], e[0])))

    def systemDistances(self):
        systems = self.SortedSystems()
        systemDistancesCalc = [ [0] * len(systems) for i in xrange(len(systems)) ]
        # For each system
        for sAIndex in xrange(0,len(systems)):
            # For each other system
            for sBIndex in xrange(0,len(systems)):
                # Calculate distances for current systems
                systemDistancesCalc[sAIndex][sBIndex] = hexutils.oddQDistance(systems[sAIndex][0],systems[sAIndex][1],systems[sBIndex][0],systems[sBIndex][1])
        return(systemDistancesCalc)

    def systemDistancesTest(self):
        systems = self.SortedSystems()
        # Distance sum list
        sumDistAll = list()
        sumDistAllPos = list()
        # For each hex row
        rowList = range(0,MAX_ROWS)
        # Shuffle rowList to not favor any specific row
        np.random.shuffle(rowList)
        for row in rowList:
            # For each hex column
            colList =range(0,MAX_COLS)
            # Shuffle colList to not favor any specific column
            np.random.shuffle(colList)
            for col in colList:
                # Sum of distances between stars
                sumDist = 0
                # Ignore hexes where there is already a system
                if ( not self.systems.has_key((row,col)) ):
                    systemDistancesCalc = self.systemDistances()
                    # Add new row for new system
                    systemDistancesCalc.append([0] * (len(self.systems) + 1))
                    # For each system
                    for sAIndex in xrange(0,len(systems)):
                        # Calculate distances for new system
                        systemDistancesCalc[sAIndex].append(hexutils.oddQDistance(row,col,systems[sAIndex][0],systems[sAIndex][1]))
                        systemDistancesCalc[len(systems)][sAIndex] = hexutils.oddQDistance(row,col,systems[sAIndex][0],systems[sAIndex][1])
                        # Sum this row
                        sumDist += int(sum(systemDistancesCalc[sAIndex]))
                    # Store sum for this options
                    sumDistAll.append(sumDist)
                    sumDistAllPos.append((row,col))
        return(sumDistAll,sumDistAllPos)

    def systemGroupDistances(self):
        # Get system groups
        systemGroups = self.systemGroups()
        # Array to hold distances between systems
        groupDistances = [ [0] * len(systemGroups) for i in xrange(len(systemGroups)) ]
        # Array to hold which two systems in the groups make up the minimum distance between them
        minDistGroupSystems = [ [0] * len(systemGroups) for i in xrange(len(systemGroups)) ]
        # For each group
        for sgAIndex in xrange(0,len(systemGroups)):
            # For each other group
            for sgBIndex in xrange(0,len(systemGroups)):
                # Don't check current group against itself
                if (sgAIndex != sgBIndex ):
                    # Assume minimum is first parining
                    minDist = hexutils.oddQDistance(systemGroups[sgAIndex][0][0],
                                                    systemGroups[sgAIndex][0][1],
                                                    systemGroups[sgBIndex][0][0],
                                                    systemGroups[sgBIndex][0][1])
                    minDistPair = (systemGroups[sgAIndex][0],systemGroups[sgBIndex][0])
                    # For each star in each group
                    for (sARow,sACol) in systemGroups[sgAIndex]:
                        # For each star in each other group
                        for (sbRow,sBCol) in systemGroups[sgBIndex]:
                            newDist = hexutils.oddQDistance(sARow,sACol,sbRow,sBCol)
                            if ( newDist < minDist ):
                                minDist = newDist
                                minDistPair = ((sARow,sACol),(sbRow,sBCol))
                    groupDistances[sgAIndex][sgBIndex] = minDist
                    minDistGroupSystems[sgAIndex][sgBIndex] = minDistPair
        return(groupDistances,minDistGroupSystems)

    def systemGroups(self):
        # Sort star systems by hex, col first, row second
        starKeys = self.SortedSystems()
        # List for placing groups
        groups = list()
        # Add stars to groups by recursively searching nearby stars
        loop1Count = 0
        while (len(starKeys) > 0):
            # Start first group with first star system remaining in list
            currentStar = starKeys[0]
            starKeys.pop(0)
            currentGroup = [currentStar]
            # Get current star neighboring hexes
            neighborSystems = self.systemNeighbors(currentStar[0],currentStar[1])
            # For all neighbor systems
            loop2Count = 0
            while (len(neighborSystems) > 0):
                try:
                    # Add to current group and remove from ungrouped list
                    currentGroup.append(starKeys.pop(starKeys.index(neighborSystems[0])))
                    # Add neighbor's neighbors to search list
                    for ns in self.systemNeighbors(neighborSystems[0][0],neighborSystems[0][1]):
                        neighborSystems.append(ns)
                except ValueError:
                    pass
                # Remove from neighboring systems search list
                neighborSystems.pop(0)
                # Catch runaway loop
                loop2Count += 1
                if (loop2Count>100):
                    raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
            groups.append(currentGroup)
            # Catch runaway loop
            loop1Count += 1
            if (loop1Count>100):
                raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
        return(groups)

    def systemNeighbors(self,row,col):
        # Get neighboring hexes
        neighborHexes = hexutils.oddQNeighbors(row,col)
        # Container for neighboring star systems
        neighborSystems = list()
        for nh in neighborHexes:
            # Actual systems have index in keylist
            try:
                self.systems.keys().index(nh)
                # Get current star neighboring star systems
                neighborSystems.append(nh)
            except ValueError:
                    pass
        return(neighborSystems)