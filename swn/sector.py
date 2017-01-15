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
        self.name = exception.arg_check(name,str,argDefault='Default Name')
        # Roll information
        self.corporations = list()
        self.heresies = list()
        self.parties = list()
        self.religions = list()
        self.systems = dict()

    def add_blank_system(self,sName,sRow,sCol):
        if (not self.hex_empty(sRow,sCol)):
            raise exception.ExistingDictKey((sRow,sCol))
        else:
            self.systems[(sRow,sCol)] = system.System(name = sName,
                                                      stars = list(),
                                                      objects = list(),
                                                      worlds = list())

    def hex_empty(self,sRow,sCol):
        return(not self.systems.has_key((sRow,sCol)))

    def print_corporations(self):
        # Create table
        table = text.Table(self.name + ' - ' + 'Sector Corporations')
        # Add headings
        table.add_heading('Index')
        table.add_heading('Corporation')
        table.add_heading('Business')
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
            table.add_row(row)
            # Update corporation index
            cIndex += 1
        # Print table
        table.print_text()

    def print_religions(self):
        # Create table
        table = text.Table(self.name + ' - ' + 'Sector Religions')
        # Add headings
        table.add_heading('Index')
        table.add_heading('Evolution')
        table.add_heading('Leadership')
        table.add_heading('Origin Tradition')
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
            table.add_row(row)
            # Update index
            rIndex += 1
        # Print table
        table.print_text()

    def print_sector_info(self):
        # Create table
        table = text.Table(self.name + ' - ' + 'Sector Info')
        # Add headings
        table.add_heading('Index')
        table.add_heading('Hex')
        table.add_heading('System')
        table.add_heading('World')
        table.add_heading('Atmosphere')
        table.add_heading('Biosphere')
        table.add_heading('Population')
        table.add_heading('Pop. Alt.','R')
        table.add_heading('Tags')
        table.add_heading('Temperature')
        table.add_heading('TL')
        # Add rows
        wIndex = 1
        for systemKey in self.sorted_systems():
            system = self.systems[systemKey]
            # Keep track of first world in system so we only print the index,
            # hex, and system name for the first entry
            firstWorld = True
            for w in system.sorted_worlds():
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
                row.append(w.population_alt_text())
                # Tags
                row.append(w.tags[0] + ', ' + w.tags[1])
                # Temperature
                row.append(w.temperature)
                # TL
                row.append(w.techLevel)
                # Add row
                table.add_row(row)
                # Update world index
                wIndex += 1
        # Print table
        table.print_text()

    def print_sector_map(self,
                       coords = None):
        # Process arguments
        coords = exception.arg_check(coords,bool,False)
        # Create hexmap
        hexMap = text.HexMap(title  = self.name + ' - ' + 'Sector Map',
                             size   = text.SMALL_MAP,
                             rows   = MAX_ROWS,
                             cols   = MAX_COLS,
                             coords = coords)
        # Add systems to map
        sIndex = 1
        for systemKey in self.sorted_systems():
            (row,col) = systemKey
            hexMap.add_label(str(sIndex),row,col)
            sIndex += 1
        # Print hexmap
        hexMap.print_text()

    def sorted_systems(self):
        return(sorted(self.systems.iterkeys(),key=lambda e: (e[1], e[0])))

    def system_distances(self):
        systems = self.sorted_systems()
        systemDistancesCalc = [ [0] * len(systems) for i in xrange(len(systems)) ]
        # For each system
        for sAIndex in xrange(0,len(systems)):
            # For each other system
            for sBIndex in xrange(0,len(systems)):
                # Calculate distances for current systems
                systemDistancesCalc[sAIndex][sBIndex] = hexutils.odd_q_distance(systems[sAIndex][0],systems[sAIndex][1],systems[sBIndex][0],systems[sBIndex][1])
        return(systemDistancesCalc)

    def system_distances_test(self):
        systems = self.sorted_systems()
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
                    systemDistancesCalc = self.system_distances()
                    # Add new row for new system
                    systemDistancesCalc.append([0] * (len(self.systems) + 1))
                    # For each system
                    for sAIndex in xrange(0,len(systems)):
                        # Calculate distances for new system
                        systemDistancesCalc[sAIndex].append(hexutils.odd_q_distance(row,col,systems[sAIndex][0],systems[sAIndex][1]))
                        systemDistancesCalc[len(systems)][sAIndex] = hexutils.odd_q_distance(row,col,systems[sAIndex][0],systems[sAIndex][1])
                        # Sum this row
                        sumDist += int(sum(systemDistancesCalc[sAIndex]))
                    # Store sum for this options
                    sumDistAll.append(sumDist)
                    sumDistAllPos.append((row,col))
        return(sumDistAll,sumDistAllPos)

    def system_group_distances(self):
        # Get system groups
        systemGroups = self.system_groups()
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
                    minDist = hexutils.odd_q_distance(systemGroups[sgAIndex][0][0],
                                                    systemGroups[sgAIndex][0][1],
                                                    systemGroups[sgBIndex][0][0],
                                                    systemGroups[sgBIndex][0][1])
                    minDistPair = (systemGroups[sgAIndex][0],systemGroups[sgBIndex][0])
                    # For each star in each group
                    for (sARow,sACol) in systemGroups[sgAIndex]:
                        # For each star in each other group
                        for (sbRow,sBCol) in systemGroups[sgBIndex]:
                            newDist = hexutils.odd_q_distance(sARow,sACol,sbRow,sBCol)
                            if ( newDist < minDist ):
                                minDist = newDist
                                minDistPair = ((sARow,sACol),(sbRow,sBCol))
                    groupDistances[sgAIndex][sgBIndex] = minDist
                    minDistGroupSystems[sgAIndex][sgBIndex] = minDistPair
        return(groupDistances,minDistGroupSystems)

    def system_groups(self):
        # Sort star systems by hex, col first, row second
        starKeys = self.sorted_systems()
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
            neighborSystems = self.system_neighbors(currentStar[0],currentStar[1])
            # For all neighbor systems
            loop2Count = 0
            while (len(neighborSystems) > 0):
                try:
                    # Add to current group and remove from ungrouped list
                    currentGroup.append(starKeys.pop(starKeys.index(neighborSystems[0])))
                    # Add neighbor's neighbors to search list
                    for ns in self.system_neighbors(neighborSystems[0][0],neighborSystems[0][1]):
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

    def system_neighbors(self,row,col):
        # Get neighboring hexes
        neighborHexes = hexutils.odd_q_neighbors(row,col)
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