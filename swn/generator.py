#!/usr/bin/env python

from __future__ import print_function

import numpy as np

import corporation
import exception
import hexutils
import name
import random
import religion
import sector
import star
import system
import world

MAX_LOOP_ITER    = 100
MAX_WORLDS       = 36
MAX_CORPORATIONS = 20
MAX_RELIGIONS    = 20

# Grouping method for placing stars after the first 20
# 0: Completely Random
# 1: Minimize the sum of distances between all systems
# 2: Maximize the sum of distances between all systems
# 3: 1/4 between min and max of the sum of distances between all systems
# 4: 1/3 between min and max of the sum of distances between all systems
# 5: 1/2 between min and max of the sum of distances between all systems
# 6: Link groups of stars together by joining the groups with the
#    furthest nearest neighbors first
# 7: Link groups of stars together, starting with the smallest,  
#    linking to their nearest
# 8: Link groups of stars together, starting with the largest, 
#    linking to their nearest
GROUPING_METHOD = 8

# Generator class --------------------------------------------------------------
class Generator(object):
    def __init__(self):
        self.seed = random.randomSeed()

    def corporation(self):
        name         = corporation.TABLE_NAME[random.diceRoll(1,25)]
        organization = corporation.TABLE_ORGANIZATION[random.diceRoll(1,25)]
        business     = corporation.TABLE_BUSINESS[random.diceRoll(1,50)]
        newCorporation = corporation.Corporation(name,organization,business)
        return(newCorporation)

    def nameSector(self):
        sectorName  = np.random.choice(name.sectorFirstNameList) + ' '
        sectorName += np.random.choice(name.sectorSecondNameList)
        sectorName += np.random.choice(['',' I',' II',' III',' IV',' V',' VI',' VII',' VIII',' IX',' X'])
        return(sectorName)

    def nameSystem(self):
        systemName = np.random.choice(name.starNameList)
        return(systemName)

    def nameWorld(self):
        worldName = np.random.choice(name.worldNameList)
        return(worldName)

    def religion(self):
        evolution   = religion.TABLE_EVOLUTION[random.diceRoll(1,8)]
        leadership  = religion.TABLE_LEADERSHIP[random.diceRoll(1,6)]
        origin      = religion.TABLE_ORIGIN_TRADITION[random.diceRoll(1,12)]
        newReligion = religion.Religion(evolution,leadership,origin)
        return(newReligion)

    def load(self):
        pass

    def save(self,fName):
        pass

    def sector(self,
               groupingMethod = GROUPING_METHOD):
        # Generate random sector name
        newsectorName = self.nameSector()
        # Create new sector object
        newSector = sector.Sector(newsectorName)
        # Generate number of stars
        numStars = random.diceRoll(1,10,20)
        # Create list of names used
        usedNames = dict()
        # Generate first 20 star system positions ------------------------------
        loopCount = 0
        sCount = 0
        while (sCount < 20):
            # Generate row and column
            #   Subtract 1 to start numbers at 0
            row = random.diceRoll(1,10)-1
            col = random.diceRoll(1,8)-1
            # Check for empy hex
            if (newSector.hexEmpty(row,col)):
                # Hex is empty, create new star system
                # TODO: Generate random star system name
                #   TODO: Check all other system names for duplicates
                nameLoopCount = 0
                nameCheck = False
                while (not nameCheck):
                    newSystemName = self.nameSystem()
                    if ( not usedNames.has_key(newSystemName) ):
                        nameCheck = True
                    nameLoopCount += 1
                    if (nameLoopCount>100):
                        raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
                newSector.addBlankSystem(newSystemName,row,col)
                sCount += 1
            else:
                # Hex is occupied, do nothing
                pass
            # Catch runaway loop
            loopCount +=1
            if (loopCount>100):
                raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)

        # Add remaining system positions based on grouping method --------------
        # loopCount = 0
        while (sCount < numStars):
            # Get row and column that fits grouping method
            #  0: Random
            loopCount = 0
            if (groupingMethod == 0):
                while ( True ):
                    newRow = random.diceRoll(1,10)-1
                    newCol = random.diceRoll(1,8)-1
                    if ( newSector.hexEmpty(newRow,newCol) ):
                        break
                    loopCount += 1
                    if (loopCount>100):
                        raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
            # 1: Minimize the sum of distances between all systems
            elif (groupingMethod == 1):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]
            # 2: Maximize the sum of distances between all systems
            elif (groupingMethod == 2):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                (newRow,newCol) = sumDistAllPos[sumDistAll.index(max(sumDistAll))]
            # 3: 1/4 between min and max of the sum of distances between all 
            #    systems
            elif (groupingMethod == 3):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                sumDistJoined = zip(sumDistAll,sumDistAllPos)
                (newRow,newCol) = sorted(sumDistJoined)[len(sumDistJoined)/4][1]
            # 4: 1/3 between min and max of the sum of distances between all 
            #    systems
            elif (groupingMethod == 4):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                sumDistJoined = zip(sumDistAll,sumDistAllPos)
                (newRow,newCol) = sorted(sumDistJoined)[len(sumDistJoined)/3][1]
            # 5: 1/2 between min and max of the sum of distances between all 
            #    systems
            elif (groupingMethod == 5):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                sumDistJoined = zip(sumDistAll,sumDistAllPos)
                (newRow,newCol) = sorted(sumDistJoined)[len(sumDistJoined)/2][1]
            # 6: Link groups of stars together by joining the groups with the
            #    furthest nearest neighbors first
            elif (groupingMethod == 6):
                # Get groups of systems
                systemGroups = newSector.systemGroups()
                # If only one large group, do something to add variety
                if ( len(systemGroups) == 1 ):
                    # Sum system distances for all new possible positions
                    (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                    # Choose new position that maximizes sum of distances
                    (newRow,newCol) = sumDistAllPos[sumDistAll.index(max(sumDistAll))]
                else:
                    # Calculate distance between groups
                    # Calculate systems in the groups whose distance define the
                    # group distance
                    (groupDistances,minDistGroupSystems) = newSector.systemGroupDistances()
                    # Distance of each group to nearest group
                    minDist      = [0] * len(groupDistances)
                    # Index of nearest group to each group
                    minDistIndex = [0] * len(groupDistances)
                    for gAIndex in xrange(len(groupDistances)):
                        # Don't compare current group to itself during comparison
                        minDist[gAIndex]      = min(groupDistances[gAIndex][:gAIndex]+groupDistances[gAIndex][gAIndex+1:])
                        minDistIndex[gAIndex] = groupDistances[gAIndex].index(minDist[gAIndex])
                    # Group that has furthest nearest neighboring group
                    maxDistAIndex = minDist.index(max(minDist))
                    maxDistBIndex = minDistIndex[maxDistAIndex]
                    # Stars that define the distance between the groups
                    ((aRow,aCol),(bRow,bCol)) = minDistGroupSystems[maxDistAIndex][maxDistBIndex]
                    # Try places stars in the middle of a line between the groups
                    line = hexutils.oddQLine(aRow,aCol,bRow,bCol)
                    (newRow,newCol) = line[len(line)/2]
                    # Check for lines that fall outside the grid
                    if ( (newRow == sector.MAX_ROWS) or 
                         (newRow < 0) or 
                         (newCol == sector.MAX_COLS) or 
                         (newCol < 0 )):
                        # Sum system distances for all new possible positions
                        (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                        # Choose new position that maximizes sum of distances
                        (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]

            # 7: Link groups of stars together, starting with the smallest,  
            #    linking to their nearest
            elif (groupingMethod == 7):
                # Get groups of systems
                systemGroups = newSector.systemGroups()
                # Shuffle groups to not favor any specific row or column
                systemGroupsShuffled = newSector.systemGroups()
                np.random.shuffle(systemGroupsShuffled)
                # Sort systemGroups by number of stars in group
                sortedMinNumberGroups = sorted(systemGroupsShuffled,key=lambda g: len(g))
                # First smallest group
                smallestGroup = sortedMinNumberGroups[0]
                # Smallest group index in unshuffled and unsorted list
                smallestGroupIndex = systemGroups.index(smallestGroup)
                # If only one large group, do something to add variety
                if ( len(systemGroups) == 1 ):
                    # Sum system distances for all new possible positions
                    (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                    # Choose new position that maximizes sum of distances
                    (newRow,newCol) = sumDistAllPos[sumDistAll.index(max(sumDistAll))]
                else:
                    # Calculate distance between groups
                    # Calculate systems in the groups whose distance define the
                    # group distance
                    # Note this order not based off of the shuffled, sorted 
                    # list above
                    (groupDistances,minDistGroupSystems) = newSector.systemGroupDistances()
                    # Distance of smallest group to nearest group
                    minDist      = min(groupDistances[smallestGroupIndex][:smallestGroupIndex]+groupDistances[smallestGroupIndex][smallestGroupIndex+1:])
                    # Indices of min distance systems of nearest group to 
                    # smallest group
                    minDistIndex = groupDistances[smallestGroupIndex].index(minDist)
                    # Stars that define the distance between the groups
                    ((aRow,aCol),(bRow,bCol)) = minDistGroupSystems[smallestGroupIndex][minDistIndex]
                    # Try places stars in the middle of a line between the groups
                    line = hexutils.oddQLine(aRow,aCol,bRow,bCol)
                    (newRow,newCol) = line[len(line)/2]
                    # Check for lines that fall outside the grid
                    if ( (newRow == sector.MAX_ROWS) or 
                         (newRow < 0) or 
                         (newCol == sector.MAX_COLS) or 
                         (newCol < 0 )):
                        # Sum system distances for all new possible positions
                        (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                        # Choose new position that maximizes sum of distances
                        (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]
            # 8: Link groups of stars together, starting with the largest, 
            #    linking to their nearest
            elif (groupingMethod == 8):
                # Get groups of systems
                systemGroups = newSector.systemGroups()
                # Shuffle groups to not favor any specific row or column
                systemGroupsShuffled = newSector.systemGroups()
                np.random.shuffle(systemGroupsShuffled)
                # Sort systemGroups by number of stars in group
                sortedMinNumberGroups = sorted(systemGroupsShuffled,key=lambda g: len(g))
                # Last largest group
                largestGroup = sortedMinNumberGroups[len(sortedMinNumberGroups)-1]
                # largest group index in unshuffled and unsorted list
                largestGroupIndex = systemGroups.index(largestGroup)
                # If only one large group, do something to add variety
                if ( len(systemGroups) == 1 ):
                    # Sum system distances for all new possible positions
                    (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                    # Choose new position that maximizes sum of distances
                    (newRow,newCol) = sumDistAllPos[sumDistAll.index(max(sumDistAll))]
                else:
                    # Calculate distance between groups
                    # Calculate systems in the groups whose distance define the
                    # group distance
                    # Note this order not based off of the shuffled, sorted 
                    # list above
                    (groupDistances,minDistGroupSystems) = newSector.systemGroupDistances()
                    # Distance of largest group to nearest group
                    minDist      = min(groupDistances[largestGroupIndex][:largestGroupIndex]+groupDistances[largestGroupIndex][largestGroupIndex+1:])
                    # Indices of min distance systems of nearest group to 
                    # largest group
                    minDistIndex = groupDistances[largestGroupIndex].index(minDist)
                    # Stars that define the distance between the groups
                    ((aRow,aCol),(bRow,bCol)) = minDistGroupSystems[largestGroupIndex][minDistIndex]
                    # Try places stars in the middle of a line between the groups
                    line = hexutils.oddQLine(aRow,aCol,bRow,bCol)
                    (newRow,newCol) = line[len(line)/2]
                    # Check for lines that fall outside the grid
                    if ( (newRow == sector.MAX_ROWS) or 
                         (newRow < 0) or 
                         (newCol == sector.MAX_COLS) or 
                         (newCol < 0 )):
                        # Sum system distances for all new possible positions
                        (sumDistAll,sumDistAllPos) = newSector.systemDistancesTest()
                        # Choose new position that maximizes sum of distances
                        (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]
            else:
                (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]

            # Create new system
            nameLoopCount = 0
            nameCheck = False
            while (not nameCheck):
                newSystemName = self.nameSystem()
                if ( not usedNames.has_key(newSystemName) ):
                    nameCheck = True
                nameLoopCount += 1
                if (nameLoopCount>100):
                    raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
            newSector.addBlankSystem(newSystemName,newRow,newCol)
            # Update count of created stars
            sCount += 1
            # Catch runaway loop
            loopCount +=1
            if (loopCount>100):
                raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)

        # Add worlds -----------------------------------------------------------
        worldCount = 0
        for systemKey in newSector.sortedSystems():
            systemObj = newSector.systems[systemKey]
            # If world count has reached max, limit number of new worlds to one
            #    per system
            if ( worldCount < MAX_WORLDS):
                numWorlds = system.TABLE_WORLDS_PER_SYSTEM[random.diceRoll(1,10)]
                worldCount += numWorlds
            else:
                numWorlds = 1
                worldCount += numWorlds
            # Add worlds to system
            for nm in xrange(numWorlds):
                nameLoopCount = 0
                nameCheck = False
                while (not nameCheck):
                    newWorldName = self.nameWorld()
                    if ( not usedNames.has_key(newSystemName) ):
                        nameCheck = True
                    nameLoopCount += 1
                    if (nameLoopCount>100):
                        raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
                # Roll tags
                atmosphere    = world.TABLE_ATMOSPHERE[random.diceRoll(2,6)]
                biosphere     = world.TABLE_BIOSPHERE[random.diceRoll(2,6)]
                pop2d6        = random.diceRoll(2,6)
                population    = world.TABLE_POPULATION[pop2d6]
                populationAlt = np.random.randint(world.TABLE_POPULATION_ALT[pop2d6][0],
                                                  world.TABLE_POPULATION_ALT[pop2d6][1]+1)
                t1d6          = random.diceRoll(1,6)
                t1d10         = random.diceRoll(1,10)
                t2d6          = random.diceRoll(1,6)
                t2d10         = random.diceRoll(1,10)
                # Don't allow duplicate tags, reroll until a new one is generated
                loopCount = 0
                while ( (t1d6 == t2d6) and (t1d10 == t2d10) ):
                    t2d6  = random.diceRoll(1,6)
                    t2d10 = random.diceRoll(1,10)
                    # Catch runaway loop
                    loopCount +=1
                    if (loopCount>100):
                        raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
                tag1       = world.TABLE_TAGS[t1d6][t1d10]
                tag2       = world.TABLE_TAGS[t2d6][t2d10]
                techLevel  = world.TABLE_TECH_LEVEL[random.diceRoll(2,6)]
                temperatue = world.TABLE_TEMPERATURE[random.diceRoll(2,6)]
                newWorld = world.World(name          = newWorldName,
                                       atmosphere    = atmosphere,
                                       biosphere     = biosphere,
                                       population    = population,
                                       populationAlt = populationAlt,
                                       tags          = [tag1,tag2],
                                       temperature   = temperatue,
                                       techLevel     = techLevel)
                systemObj.worlds.append(newWorld)

        # Add corporations -----------------------------------------------------
        for i in xrange(MAX_CORPORATIONS):
            newSector.corporations.append(self.corporation())

        # Add religions --------------------------------------------------------
        for i in xrange(MAX_RELIGIONS):
            newSector.religions.append(self.religion())

        # Return new sector ----------------------------------------------------
        return(newSector)

    def setSeed(self,seedString):
        # Check arguments
        #   name
        if not (isinstance(seedString,str)):
            raise exception.InvalidArgType(argName,str)
        # Set seed
        random.setSeed(random.seedAlphabetDecode(seedString))
        self.seed = seedString