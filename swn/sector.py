#!/usr/bin/env python

from __future__ import print_function

import math
import numpy as np
import operator

import exception
import generator
import hexutils
import star

MAX_ROWS = 10
MAX_COLS = 8

# Sector class -----------------------------------------------------------------
class Sector(object):
    def __init__(self,
                 name):
        # Check arguments
        #   name
        if not (isinstance(name,str)):
            raise exception.InvalidClassArgType(self,'name',name,str)
        # General information
        self.name = name
        # Roll information
        self.corporations = list()
        self.heresies = list()
        self.parties = list()
        self.religions = list()
        self.stars = dict()

    def addBlankSystem(self,sName,sRow,sCol):
        if (not self.hexEmpty(sRow,sCol)):
            raise exception.ExistingDictKey((sRow,sCol))
        else:
            self.stars[(sRow,sCol)] = star.System(name = sName,
                                                  stars = list(),
                                                  planets = list(),
                                                  worlds = list())

    def hexEmpty(self,sRow,sCol):
        return(not self.stars.has_key((sRow,sCol)))

    def printCorporations(self):
        # Caclulate lengths
        #    Known lengths
        indexLen = len('Index')
        #    Lengths to check each religions for
        corporationLen = len('Corporation')
        businessLen = len('Business')
        for c in self.corporations:
            # Corporation length
            cName = c.name + ' ' + c.organization
            if ( len(cName) > corporationLen ):
                corporationLen = len(cName)
            # Business length
            if ( len(c.business) > businessLen ):
                businessLen = len(c.business)
        # Set lengths
        lineBegin    = '# '
        lineEnd      = ' #'
        lineBeginLen = len(lineBegin)
        lineEndLen   = len(lineEnd)
        sep          = ' | '
        sepLen       = len(sep)
        # Sum lengths
        lineLength  = lineBeginLen + indexLen + sepLen + corporationLen + sepLen
        lineLength += businessLen + lineEndLen
        # Print top border
        border = ''
        for i in xrange(lineLength):
            border += '#'
        print(border)
        # Print sector name
        sectorLine = border
        sectorText = ' ' + self.name + ' - ' + 'Sector Corporations' + ' '
        sectorLine = sectorLine[:1] + sectorText + sectorLine [(1+len(sectorText)):]
        print(sectorLine)
        print(border)
        # Print headings
        line = lineBegin
        line += 'Index'.ljust(indexLen)
        line += sep
        line += 'Corporation'.ljust(corporationLen)
        line += sep
        line += 'Business'.ljust(businessLen)
        line += lineEnd
        print(line)
        print(lineBegin + '-'*(lineLength-lineBeginLen-lineEndLen) + lineEnd)
        # Print corporation info
        cIndex = 0
        for c in self.corporations:
            line  = lineBegin
            line += str(cIndex).rjust(2).ljust(indexLen)
            line += sep
            cName = c.name + ' ' + c.organization
            line += cName.ljust(corporationLen)
            line += sep
            line += c.business.ljust(businessLen)
            line += lineEnd
            print(line)
            cIndex += 1
        # Print bottom border
        print(border)

    def printReligions(self):
        # Caclulate lengths
        #    Known lengths
        indexLen = len('Index')
        #    Lengths to check each religions for
        evolutionLen = len('Evolution')
        leadershipLen = len('Leadership')
        originLen = len('Origin Tradition')
        for r in self.religions:
            # Evolution length
            if ( len(r.evolution) > evolutionLen ):
                evolutionLen = len(r.evolution)
            # Leadership length
            if ( len(r.leadership) > leadershipLen ):
                leadershipLen = len(r.leadership)
            # Origin length
            if ( len(r.origin) > originLen ):
                originLen = len(r.origin)
        # Set lengths
        lineBegin    = '# '
        lineEnd      = ' #'
        lineBeginLen = len(lineBegin)
        lineEndLen   = len(lineEnd)
        sep          = ' | '
        sepLen       = len(sep)
        # Sum lengths
        lineLength  = lineBeginLen + indexLen + sepLen + evolutionLen + sepLen
        lineLength += leadershipLen + sepLen + originLen + lineEndLen
        # Print top border
        border = ''
        for i in xrange(lineLength):
            border += '#'
        print(border)
        # Print sector name
        sectorLine = border
        sectorText = ' ' + self.name + ' - ' + 'Sector Religions' + ' '
        sectorLine = sectorLine[:1] + sectorText + sectorLine [(1+len(sectorText)):]
        print(sectorLine)
        print(border)
        # Print headings
        line = lineBegin
        line += 'Index'.ljust(indexLen)
        line += sep
        line += 'Evolution'.ljust(evolutionLen)
        line += sep
        line += 'Leadership'.ljust(leadershipLen)
        line += sep
        line += 'Origin Tradition'.ljust(originLen)
        line += lineEnd
        print(line)
        print(lineBegin + '-'*(lineLength-lineBeginLen-lineEndLen) + lineEnd)
        # Print religion info
        rIndex = 0
        for r in self.religions:
            line  = lineBegin
            line += str(rIndex).rjust(2).ljust(indexLen)
            line += sep
            line += r.evolution.ljust(evolutionLen)
            line += sep
            line += r.leadership.ljust(leadershipLen)
            line += sep
            line += r.origin.ljust(originLen)
            line += lineEnd
            print(line)
            rIndex += 1
        # Print bottom border
        print(border)

    def printSectorInfo(self):
        # Calculate lengths
        #    Known lengths
        indexLen = 6
        hexLen = 5
        tlLen = 2
        #    Lengths check each world for
        systemLen = 0
        worldLen = 0
        atmosphereLen = 0
        biosphereLen = 0
        populationLen = 0
        populationAltLen = 0
        tagsLen = 0
        temperatureLen = 0
        # Check all systems
        for systemKey in self.sortedSystems():
            # System name length
            if ( len(self.stars[systemKey].name) > systemLen ):
                systemLen =  len(self.stars[systemKey].name)
            # Check all worlds
            for w in self.stars[systemKey].worlds:
                # World name length
                if ( len(w.name) > worldLen ):
                    worldLen =  len(w.name)
                # Atmosphere length
                if ( len(w.atmosphere) > atmosphereLen ):
                    atmosphereLen = len(w.atmosphere)
                # Biosphere length
                if ( len(w.biosphere) > biosphereLen ):
                    biosphereLen = len(w.biosphere)
                # Population length
                if ( len(w.population) > populationLen ):
                    populationLen = len(w.population)
                # Population alternate length
                popAltStrCommas = ''
                popAltStr = str(w.populationAlt)
                while ( len(popAltStr) > 0 ):
                    if ( len(popAltStr) < 4 ):
                        popAltStrCommas = popAltStr + popAltStrCommas
                        popAltStr = ''
                    else:
                        popAltStrCommas =  ',' + popAltStr[-3:] + popAltStrCommas
                        popAltStr = popAltStr[:-3]
                if ( len(popAltStrCommas) > populationAltLen ):
                    populationAltLen = len(popAltStrCommas)
                # Tags length
                if ( len(str(w.tags[0] + ', ' + w.tags[1])) > tagsLen ):
                    tagsLen = len(str(w.tags[0] + ', ' + w.tags[1]) )
                # Temperature length
                if ( len(w.temperature) > temperatureLen ):
                    temperatureLen = len(w.temperature)
        # Set lengths
        lineBegin    = '# '
        lineEnd      = ' #'
        lineBeginLen = len(lineBegin)
        lineEndLen   = len(lineEnd)
        sep          = ' | '
        sepLen       = len(sep)
        # Sum lengths
        lineLength  = lineBeginLen + indexLen + sepLen + hexLen + sepLen
        lineLength += systemLen + sepLen + worldLen + sepLen + atmosphereLen
        lineLength += sepLen + biosphereLen + sepLen + populationLen + sepLen
        lineLength += populationAltLen + sepLen + tagsLen + sepLen
        lineLength += temperatureLen + sepLen + tlLen + lineEndLen
        # Print border
        border = ''
        for i in xrange(lineLength):
            border += '#'
        print(border)
        # Print sector name
        sectorLine = border
        sectorText = ' ' + self.name + ' - ' + 'Sector Info' + ' '
        sectorLine = sectorLine[:1] + sectorText + sectorLine [(1+len(sectorText)):]
        print(sectorLine)
        print(border)
        # Print headings
        line = lineBegin
        line += 'Index'.ljust(indexLen)
        line += sep
        line += 'Hex'.ljust(hexLen)
        line += sep
        line += 'System'.ljust(systemLen)
        line += sep
        line += 'World'.ljust(worldLen)
        line += sep
        line += 'Atmosphere'.ljust(atmosphereLen)
        line += sep
        line += 'Biosphere'.ljust(biosphereLen)
        line += sep
        line += 'Population'.ljust(populationLen)
        line += sep
        line += 'Pop. Alt.'.ljust(populationAltLen)
        line += sep
        line += 'Tags'.ljust(tagsLen)
        line += sep
        line += 'Temperature'.ljust(temperatureLen)
        line += sep
        line += 'TL'.ljust(tlLen)
        line += lineEnd
        print(line)
        print(lineBegin + '-'*(lineLength-lineBeginLen-lineEndLen) + lineEnd)
        # Create lines
        sIndex = 0
        for systemKey in self.sortedSystems():
            wIndex = 0
            indexText = [''] * len(self.stars[systemKey].worlds)
            indexText[0] = str(sIndex)
            systemHexText = [''] * len(self.stars[systemKey].worlds)
            systemHexText[0] = '0{0}0{1}'.format(systemKey[0],systemKey[1])
            systemNameText = [''] * len(self.stars[systemKey].worlds)
            systemNameText[0] = self.stars[systemKey].name
            for w in self.stars[systemKey].worlds:
                line = lineBegin
                line += indexText[wIndex].rjust(2).ljust(indexLen)
                line += sep
                line += systemHexText[wIndex].ljust(hexLen)
                line += sep
                line += systemNameText[wIndex].ljust(systemLen)
                line += sep
                line += w.name.ljust(worldLen)
                line += sep
                line += w.atmosphere.ljust(atmosphereLen)
                line += sep
                line += w.biosphere.ljust(biosphereLen)
                line += sep
                line += w.population.ljust(populationLen)
                line += sep
                popAltStrCommas = ''
                popAltStr = str(w.populationAlt)
                # All digits
                #while ( len(popAltStr) > 0 ):
                #    if ( len(popAltStr) < 4 ):
                #        popAltStrCommas = popAltStr + popAltStrCommas
                #        popAltStr = ''
                #    else:
                #        # All digits
                #        popAltStrCommas = ',' + popAltStr[-3:] + popAltStrCommas
                #        popAltStr = popAltStr[:-3]
                # Three significant figures
                popAltStrRev = popAltStr[::-1]
                cCount = 0
                while ( len(popAltStrRev) > 0 ):
                    if ( len(popAltStrRev) > 3 ):
                        popAltStrCommas = str(0) + popAltStrCommas
                    else: 
                        popAltStrCommas = popAltStrRev[0]+ popAltStrCommas
                    popAltStrRev = popAltStrRev[1:]
                    cCount += 1
                    if ( (cCount == 3) and (len(popAltStrRev) > 0) ): 
                        popAltStrCommas = ',' + popAltStrCommas
                        cCount = 0
                line += popAltStrCommas.rjust(populationAltLen)
                line += sep
                line += str(w.tags[0] + ', ' + w.tags[1]).ljust(tagsLen)
                line += sep
                line += w.temperature.ljust(temperatureLen)
                line += sep
                line += w.techLevel.ljust(tlLen)
                line += lineEnd
                # Print line
                print(line)
                wIndex += 1
            sIndex += 1
        print(border)

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
            starKeys = self.sortedSystems()
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

    def sortedSystems(self):
        return(sorted(self.stars.iterkeys(),key=lambda e: (e[1], e[0])))

    def systemDistances(self):
        systems = self.sortedSystems()
        systemDistancesCalc = [ [0] * len(systems) for i in xrange(len(systems)) ]
        # For each system
        for sAIndex in xrange(0,len(systems)):
            # For each other system
            for sBIndex in xrange(0,len(systems)):
                # Calculate distances for current systems
                systemDistancesCalc[sAIndex][sBIndex] = hexutils.oddQDistance(systems[sAIndex][0],systems[sAIndex][1],systems[sBIndex][0],systems[sBIndex][1])
        return(systemDistancesCalc)

    def systemDistancesTest(self):
        systems = self.sortedSystems()
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
                if ( not self.stars.has_key((row,col)) ):
                    systemDistancesCalc = self.systemDistances()
                    # Add new row for new system
                    systemDistancesCalc.append([0] * (len(self.stars) + 1))
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
        starKeys = self.sortedSystems()
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
                self.stars.keys().index(nh)
                # Get current star neighboring star systems
                neighborSystems.append(nh)
            except ValueError:
                    pass
        return(neighborSystems)