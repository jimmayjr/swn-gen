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

    def PrintSectorMap(self,
                       coords = None):
        # Process arguments
        coords = exception.ArgCheck(coords,bool,False)
        # Create hexmap
        hexMap = text.HexMap(title  = self.name + ' - ' + 'Sector Map',
                             size   = text.SMALL_MAP,
                             rows   = MAX_ROWS,
                             cols   = MAX_COLS,
                             coords = coords)
        # Add systems to map
        sIndex = 1
        for systemKey in self.SortedSystems():
            (row,col) = systemKey
            hexMap.AddLabel(str(sIndex),row,col)
            sIndex += 1
        # Print hexmap
        hexMap.Print()

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