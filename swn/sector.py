#!/usr/bin/env python

from __future__ import print_function

import math
import numpy as np
import operator

import exception
import generator
import hexutils
import image
import orbitalobject
import system
import text


SECTOR_MAJOR_ROW = 0
SECTOR_MAJOR_COL = 0
SECTOR_ROWS = 10
SECTOR_COLS = 8

# Sector class -----------------------------------------------------------------
## Sector class.
#
# Class to hold a SWN sector.
class Sector(object):
    ## Sector constructor.
    #  @param self     The object pointer.
    #  @param majorRow Major row of sector.
    #  @param majorCol Major column of sector.
    #  @param rows     Number of rows in sector.
    #  @param cols     Number of columns in sector.
    def __init__(self,
                 name,
                 majorRow = None,
                 majorCol = None,
                 rows     = None,
                 cols     = None):
        # General information
        self.name     = exception.arg_check(name,     str, 'Default Name')
        self.majorRow = exception.arg_check(majorRow, int, SECTOR_MAJOR_ROW)
        self.majorCol = exception.arg_check(majorCol, int, SECTOR_MAJOR_COL)
        self._rows    = exception.arg_check(rows,     int, SECTOR_ROWS)
        self._cols    = exception.arg_check(cols,     int, SECTOR_COLS)
        # Roll information
        self.corporations = list()
        self.heresies     = list()
        self.parties      = list()
        self.religions    = list()
        self.systems      = dict()
        # Custom information
        self.highlights = list()
        self.routes     = list()
        # Images
        self.images = image.SectorImage(self.majorRow,
                                        self.majorCol,
                                        self._rows,
                                        self._cols)

    ## Add a blank system.
    #
    #  Add a blank system to a sector.
    def add_blank_system(self,sName,sRow,sCol):
        if (not self.hex_empty(sRow,sCol)):
            raise exception.ExistingDictKey((sRow,sCol))
        else:
            self.systems[(sRow,sCol)] = system.System(name = sName,
                                                      stars = list(),
                                                      objects = list(),
                                                      worlds = list())

    ## Draw sector
    def draw_sector(self):
        self.images.draw_sector()


    ## Hex empty check.
    #  Check if a sector hex is empty (True) or has a system already (False).
    def hex_empty(self,sRow,sCol):
        return(not self.systems.has_key((sRow,sCol)))

    ## Print table of corporations.
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

    ## Print system orbit maps.
    def print_orbit_maps(self):
        columnHeight = 3
        # Create orbit map for each system
        for systemKey in self.sorted_systems():
            starSystem = self.systems[systemKey]
            # Initial empty map
            systemMap = text.OrbitMap(starSystem.name + ' - ' + 'Orbit Map')
            # Determine maximum number of objects per orbit
            # Start with the number of stars in this system
            maxObjects = len(starSystem.stars)
            # Check orbital objects
            for o in starSystem.objects:
                # Start with 1 for the planet or asteroid belt
                orbitCount = 1
                if ( type(o) is orbitalobject.Planet ):
                    # For each station
                    for s in o.stations:
                        orbitCount += 1
                    # For each moon
                    for m in o.moons:
                        orbitCount += 1
                maxObjects = max(maxObjects,orbitCount)
            # Add stars
            orbitList = list()
            for s in starSystem.stars:
                orbitList.append(s.color.upper()[0]+str(s.spectralSubclass))
            systemMap.add_orbit(orbitList)
            # Add planets and asteroid belts
            for o in starSystem.objects:
                orbitList = list()
                # Add planet
                if ( type(o) is orbitalobject.Planet ):
                    planetString = orbitalobject.TABLE_ORBITAL_OBJECT_ABBREVIATIONS[o.objectType]
                    # Signify if planet is a world
                    if ( o.world is not None ):
                        worldIndex = starSystem.worlds.index(o.world)
                        orbitList.append(planetString + '-W' + str(worldIndex+1))
                    else:
                        orbitList.append(planetString)
                    # Satellites
                    satelliteList = list()
                    # For each station
                    for s in o.stations:
                        stationString = orbitalobject.TABLE_ORBITAL_OBJECT_ABBREVIATIONS[s.objectType]
                        # Signify if station is a world
                        if ( s.world is not None ):
                            worldIndex = starSystem.worlds.index(s.world)
                            satelliteList.append(stationString + '-W' + str(worldIndex+1))
                        else:
                            satelliteList.append(stationString)
                    # For each moon
                    for m in o.moons:
                        moonString = orbitalobject.TABLE_ORBITAL_OBJECT_ABBREVIATIONS[m.objectType]
                        # Signify if moon is a world
                        if ( m.world is not None ):
                            worldIndex = starSystem.worlds.index(m.world)
                            satelliteList.append(moonString + '-W' + str(worldIndex+1))
                        else:
                            satelliteList.append(moonString)
                    # Add planets to list
                    systemMap.add_orbit(orbitList,satelliteList)
                # Add asteroid belt
                elif ( type(o) is orbitalobject.AsteroidBelt ):
                    # Determine abbreviation for belt
                    beltString = orbitalobject.TABLE_ORBITAL_OBJECT_ABBREVIATIONS[o.objectType]
                    # Fill orbit to maxObjects length with belt abbreviation
                    orbitList += [beltString for objectNum in xrange(maxObjects)]
                    systemMap.add_orbit(orbitList)
            # Print orbit map
            systemMap.print_text()

    ## Print table of religions.
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

    ## Print table of sector systems information.
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

    ## Print sector hex map.
    def print_sector_map(self,
                       coords = None):
        # Process arguments
        coords = exception.arg_check(coords,bool,False)
        # Create hexmap
        hexMap = text.HexMap(title  = self.name + ' - ' + 'Sector Map',
                             size   = text.SMALL_MAP,
                             rows   = SECTOR_ROWS,
                             cols   = SECTOR_COLS,
                             coords = coords)
        # Add systems to map
        sIndex = 1
        for systemKey in self.sorted_systems():
            (row,col) = systemKey
            hexMap.add_label(str(sIndex),row,col)
            sIndex += 1
        # Print hexmap
        hexMap.print_text()

    ## Sort systems by hex numbering.
    def sorted_systems(self):
        return(sorted(self.systems.iterkeys(),key=lambda e: (e[1], e[0])))

    ## Calculate hex distances between all systems.
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

    ## Test distances between all systems if a new system is added.
    def system_distances_test(self):
        systems = self.sorted_systems()
        # Distance sum list
        sumDistAll = list()
        sumDistAllPos = list()
        # For each hex row
        rowList = range(0,SECTOR_ROWS)
        # Shuffle rowList to not favor any specific row
        np.random.shuffle(rowList)
        for row in rowList:
            # For each hex column
            colList =range(0,SECTOR_COLS)
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

    ## Calculate distances between groups of systems.
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

    ## Find groups of systems.
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

    ## Find neighbors of systems.
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