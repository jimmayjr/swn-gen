#!/usr/bin/env python

from __future__ import print_function

import numpy as np
import operator

import corporation
import exception
import hexutils
import name
import orbitalobject
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
        self.seed = random.random_seed()

    def corporation(self):
        name         = corporation.TABLE_NAME[random.dice_roll(1,25)]
        organization = corporation.TABLE_ORGANIZATION[random.dice_roll(1,25)]
        business     = corporation.TABLE_BUSINESS[random.dice_roll(1,50)]
        newCorporation = corporation.Corporation(name,organization,business)
        return(newCorporation)

    def load(self):
        raise Exception('Not implemented yet.')

    def moons(self,d20):
        numSmallMoons  = orbitalobject.TABLE_SMALL_MOONS[d20]
        numMediumMoons = orbitalobject.TABLE_MEDIUM_MOONS[d20]
        moonList  = [orbitalobject.Moon(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['SMALL_MOON']) for sm in xrange(numSmallMoons)]
        moonList += [orbitalobject.Moon(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['MEDIUM_MOON']) for mm in xrange(numMediumMoons)]
        np.random.shuffle(moonList)
        return(moonList)

    def name_sector(self):
        sectorName  = np.random.choice(name.sectorFirstNameList) + ' '
        sectorName += np.random.choice(name.sectorSecondNameList)
        sectorName += np.random.choice(['',' I',' II',' III',' IV',' V',' VI',' VII',' VIII',' IX',' X'])
        return(sectorName)

    def name_system(self):
        systemName = np.random.choice(name.starNameList)
        return(systemName)

    def name_world(self):
        worldName = np.random.choice(name.worldNameList)
        return(worldName)

    def religion(self):
        evolution   = religion.TABLE_EVOLUTION[random.dice_roll(1,8)]
        leadership  = religion.TABLE_LEADERSHIP[random.dice_roll(1,6)]
        origin      = religion.TABLE_ORIGIN_TRADITION[random.dice_roll(1,12)]
        newReligion = religion.Religion(evolution,leadership,origin)
        return(newReligion)    

    def rings(self,d20):
        return(orbitalobject.TABLE_MINOR_RINGS[d20])

    def save(self,fName):
        raise Exception('Not implemented yet.')

    def sector(self,
               groupingMethod = GROUPING_METHOD):
        # Generate random sector name
        newsectorName = self.name_sector()
        # Create new sector object
        newSector = sector.Sector(newsectorName,
                                  sector.SECTOR_MAJOR_ROW,
                                  sector.SECTOR_MAJOR_COL,
                                  sector.SECTOR_ROWS,
                                  sector.SECTOR_COLS)
        # Generate number of stars
        numStars = random.dice_roll(1,10,20)
        # Create list of names used
        usedNames = dict()
        # Generate first 20 star system positions ------------------------------
        loopCount = 0
        sCount = 0
        while (sCount < 20):
            # Generate row and column
            #   Subtract 1 to start numbers at 0
            row = random.dice_roll(1,10)-1
            col = random.dice_roll(1,8)-1
            # Check for empy hex
            if (newSector.hex_empty(row,col)):
                # Hex is empty, create new star system
                # TODO: Generate random star system name
                #   TODO: Check all other system names for duplicates
                nameLoopCount = 0
                nameCheck = False
                while (not nameCheck):
                    newSystemName = self.name_system()
                    if ( not usedNames.has_key(newSystemName) ):
                        nameCheck = True
                    nameLoopCount += 1
                    if (nameLoopCount>100):
                        raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
                newSector.add_blank_system(newSystemName,row,col)
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
                    newRow = random.dice_roll(1,10)-1
                    newCol = random.dice_roll(1,8)-1
                    if ( newSector.hex_empty(newRow,newCol) ):
                        break
                    loopCount += 1
                    if (loopCount>100):
                        raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
            # 1: Minimize the sum of distances between all systems
            elif (groupingMethod == 1):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]
            # 2: Maximize the sum of distances between all systems
            elif (groupingMethod == 2):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                (newRow,newCol) = sumDistAllPos[sumDistAll.index(max(sumDistAll))]
            # 3: 1/4 between min and max of the sum of distances between all 
            #    systems
            elif (groupingMethod == 3):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                sumDistJoined = zip(sumDistAll,sumDistAllPos)
                (newRow,newCol) = sorted(sumDistJoined)[len(sumDistJoined)/4][1]
            # 4: 1/3 between min and max of the sum of distances between all 
            #    systems
            elif (groupingMethod == 4):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                sumDistJoined = zip(sumDistAll,sumDistAllPos)
                (newRow,newCol) = sorted(sumDistJoined)[len(sumDistJoined)/3][1]
            # 5: 1/2 between min and max of the sum of distances between all 
            #    systems
            elif (groupingMethod == 5):
                # Sum system distances for all new possible positions
                (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                sumDistJoined = zip(sumDistAll,sumDistAllPos)
                (newRow,newCol) = sorted(sumDistJoined)[len(sumDistJoined)/2][1]
            # 6: Link groups of stars together by joining the groups with the
            #    furthest nearest neighbors first
            elif (groupingMethod == 6):
                # Get groups of systems
                systemGroups = newSector.system_groups()
                # If only one large group, do something to add variety
                if ( len(systemGroups) == 1 ):
                    # Sum system distances for all new possible positions
                    (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                    # Choose new position that maximizes sum of distances
                    (newRow,newCol) = sumDistAllPos[sumDistAll.index(max(sumDistAll))]
                else:
                    # Calculate distance between groups
                    # Calculate systems in the groups whose distance define the
                    # group distance
                    (groupDistances,minDistGroupSystems) = newSector.system_group_distances()
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
                    line = hexutils.odd_q_line(aRow,aCol,bRow,bCol)
                    (newRow,newCol) = line[len(line)/2]
                    # Check for lines that fall outside the grid
                    if ( (newRow == sector.SECTOR_ROWS) or 
                         (newRow < 0) or 
                         (newCol == sector.SECTOR_COLS) or 
                         (newCol < 0 )):
                        # Sum system distances for all new possible positions
                        (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                        # Choose new position that maximizes sum of distances
                        (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]

            # 7: Link groups of stars together, starting with the smallest,  
            #    linking to their nearest
            elif (groupingMethod == 7):
                # Get groups of systems
                systemGroups = newSector.system_groups()
                # Shuffle groups to not favor any specific row or column
                systemGroupsShuffled = newSector.system_groups()
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
                    (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                    # Choose new position that maximizes sum of distances
                    (newRow,newCol) = sumDistAllPos[sumDistAll.index(max(sumDistAll))]
                else:
                    # Calculate distance between groups
                    # Calculate systems in the groups whose distance define the
                    # group distance
                    # Note this order not based off of the shuffled, sorted 
                    # list above
                    (groupDistances,minDistGroupSystems) = newSector.system_group_distances()
                    # Distance of smallest group to nearest group
                    minDist      = min(groupDistances[smallestGroupIndex][:smallestGroupIndex]+groupDistances[smallestGroupIndex][smallestGroupIndex+1:])
                    # Indices of min distance systems of nearest group to 
                    # smallest group
                    minDistIndex = groupDistances[smallestGroupIndex].index(minDist)
                    # Stars that define the distance between the groups
                    ((aRow,aCol),(bRow,bCol)) = minDistGroupSystems[smallestGroupIndex][minDistIndex]
                    # Try places stars in the middle of a line between the groups
                    line = hexutils.odd_q_line(aRow,aCol,bRow,bCol)
                    (newRow,newCol) = line[len(line)/2]
                    # Check for lines that fall outside the grid
                    if ( (newRow == sector.SECTOR_ROWS) or 
                         (newRow < 0) or 
                         (newCol == sector.SECTOR_COLS) or 
                         (newCol < 0 )):
                        # Sum system distances for all new possible positions
                        (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                        # Choose new position that maximizes sum of distances
                        (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]
            # 8: Link groups of stars together, starting with the largest, 
            #    linking to their nearest
            elif (groupingMethod == 8):
                # Get groups of systems
                systemGroups = newSector.system_groups()
                # Shuffle groups to not favor any specific row or column
                systemGroupsShuffled = newSector.system_groups()
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
                    (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                    # Choose new position that maximizes sum of distances
                    (newRow,newCol) = sumDistAllPos[sumDistAll.index(max(sumDistAll))]
                else:
                    # Calculate distance between groups
                    # Calculate systems in the groups whose distance define the
                    # group distance
                    # Note this order not based off of the shuffled, sorted 
                    # list above
                    (groupDistances,minDistGroupSystems) = newSector.system_group_distances()
                    # Distance of largest group to nearest group
                    minDist      = min(groupDistances[largestGroupIndex][:largestGroupIndex]+groupDistances[largestGroupIndex][largestGroupIndex+1:])
                    # Indices of min distance systems of nearest group to 
                    # largest group
                    minDistIndex = groupDistances[largestGroupIndex].index(minDist)
                    # Stars that define the distance between the groups
                    ((aRow,aCol),(bRow,bCol)) = minDistGroupSystems[largestGroupIndex][minDistIndex]
                    # Try places stars in the middle of a line between the groups
                    line = hexutils.odd_q_line(aRow,aCol,bRow,bCol)
                    (newRow,newCol) = line[len(line)/2]
                    # Check for lines that fall outside the grid
                    if ( (newRow == sector.SECTOR_ROWS) or 
                         (newRow < 0) or 
                         (newCol == sector.SECTOR_COLS) or 
                         (newCol < 0 )):
                        # Sum system distances for all new possible positions
                        (sumDistAll,sumDistAllPos) = newSector.system_distances_test()
                        # Choose new position that maximizes sum of distances
                        (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]
            else:
                (newRow,newCol) = sumDistAllPos[sumDistAll.index(min(sumDistAll))]

            # Create new system
            nameLoopCount = 0
            nameCheck = False
            while (not nameCheck):
                newSystemName = self.name_system()
                if ( not usedNames.has_key(newSystemName) ):
                    nameCheck = True
                nameLoopCount += 1
                if (nameLoopCount>100):
                    raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
            newSector.add_blank_system(newSystemName,newRow,newCol)
            # Update count of created systems
            sCount += 1
            # Catch runaway loop
            loopCount +=1
            if (loopCount>100):
                raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)

        # Add worlds -----------------------------------------------------------
        worldCount = 0
        for systemKey in newSector.sorted_systems():
            systemObj = newSector.hexes[systemKey].system
            # If world count has reached max, limit number of new worlds to one
            #    per system
            if ( worldCount < MAX_WORLDS):
                numWorlds = system.TABLE_WORLDS[random.dice_roll(1,10)]
                worldCount += numWorlds
            else:
                numWorlds = 1
                worldCount += numWorlds
            # Add worlds to system
            for nm in xrange(numWorlds):
                nameLoopCount = 0
                nameCheck = False
                while (not nameCheck):
                    newWorldName = self.name_world()
                    if ( not usedNames.has_key(newSystemName) ):
                        nameCheck = True
                    nameLoopCount += 1
                    if (nameLoopCount>100):
                        raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
                # Roll tags
                atmosphere    = world.TABLE_ATMOSPHERE[random.dice_roll(2,6)]
                biosphere     = world.TABLE_BIOSPHERE[random.dice_roll(2,6)]
                pop2d6        = random.dice_roll(2,6)
                population    = world.TABLE_POPULATION[pop2d6]
                populationAlt = np.random.randint(world.TABLE_POPULATION_ALT[pop2d6][0],
                                                  world.TABLE_POPULATION_ALT[pop2d6][1]+1)
                t1d6          = random.dice_roll(1,6)
                t1d10         = random.dice_roll(1,10)
                t2d6          = random.dice_roll(1,6)
                t2d10         = random.dice_roll(1,10)
                # Don't allow duplicate tags, reroll until a new one is generated
                loopCount = 0
                while ( (t1d6 == t2d6) and (t1d10 == t2d10) ):
                    t2d6  = random.dice_roll(1,6)
                    t2d10 = random.dice_roll(1,10)
                    # Catch runaway loop
                    loopCount +=1
                    if (loopCount>100):
                        raise exception.MaxLoopIterationsExceed(MAX_LOOP_ITER)
                tag1       = world.TABLE_TAGS[t1d6][t1d10]
                tag2       = world.TABLE_TAGS[t2d6][t2d10]
                techLevel  = world.TABLE_TECH_LEVEL[random.dice_roll(2,6)]
                temperatue = world.TABLE_TEMPERATURE[random.dice_roll(2,6)]
                newWorld = world.World(name          = newWorldName,
                                       atmosphere    = atmosphere,
                                       biosphere     = biosphere,
                                       population    = population,
                                       populationAlt = populationAlt,
                                       tags          = [tag1,tag2],
                                       temperature   = temperatue,
                                       techLevel     = techLevel)
                systemObj.worlds.append(newWorld)

        # Fill system data -----------------------------------------------------
        # Use one roll star system (ORSS) rules
        for systemKey in newSector.sorted_systems():
            # Get current system
            systemObj = newSector.hexes[systemKey].system
            # Rolls (ORSS)
            d4  = random.dice_roll(1,4)
            d6  = random.dice_roll(1,6)
            d8  = random.dice_roll(1,8)
            d10 = random.dice_roll(1,10)
            d12 = random.dice_roll(1,12)
            d20 = random.dice_roll(1,20)
            # Get main world from system (i.e. the first in the list with the highest TL)
            mainWorld = max(systemObj.worlds,key=lambda w: world.TABLE_TECH_LEVEL_REVERSE[w.techLevel])
            # Get main world orbit temperature mod
            d12Mod = d12 + world.TABLE_MAIN_WORLD_ORBIT_TEMP_MOD[mainWorld.temperature]
            # At this point, the modified d12 roll cannot be lower than 1
            if (d12Mod < 1):
                d12Mod = 1
            # Check d6 to determine usage of d4 and d12 rolls (ORSS)
            d4Mod = d4
            #    If d6 is 1, d4 becomes single red dwarf star system (ORSS)
            if ( d6 == 1):
                d4Mod  = 1
                d12Mod = 0
            #    If d6 is 2 or 3 and d4 is 4 add 12 to d12 (ORSS)
            elif ( (d6==2) or (d6==3) ):
                if ( d4 == 4):
                    d12Mod += 12
            #    If d6 is 4, add 1 to d4
            elif ( d6 == 6):
                d4Mod += 1
            # Main world orbit
            #    d6 table is base orbit position
            mainOrbit  = system.TABLE_MAIN_WORLD_ORBIT[d6]
            #    d12 table modifies orbit position
            mainOrbit += system.TABLE_MAIN_WORLD_ORBIT_MOD[d12Mod]
            # First star color and spectral subclass
            color            = star.TABLE_COLOR[star.TABLE_COLOR_ID[d12Mod]]
            colorText        = star.TABLE_COLOR_TEXT[d12Mod]
            spectralSubclass = star.TABLE_SPECTRAL_SUBCLASS[d10]
            # Add first star
            systemObj.stars.append(star.Star(color,colorText,spectralSubclass))
            # Use modified d4 to determine if there should be a second star (ORSS)
            numStars = system.TABLE_STARS[d4Mod]
            # Add 2nd star if necessary (ORSS)
            if ( numStars > 1 ):
                # 2nd star has +4 to existing d12 roll(ORSS)
                d12Mod += 4
                # 2nd star has alternate d10 roll (ORSS)    
                d10Mod   = random.dice_roll(1,10)
                # d12 table modifies orbit position (ORSS)
                mainOrbit += system.TABLE_MAIN_WORLD_ORBIT_MOD[d12Mod]
                # Second star color and spectral subclass (ORSS)
                color            = star.TABLE_COLOR[star.TABLE_COLOR_ID[d12Mod]]
                colorText        = star.TABLE_COLOR_TEXT[d12Mod]
                spectralSubclass = star.TABLE_SPECTRAL_SUBCLASS[d10Mod]
                # Add star
                systemObj.stars.append(star.Star(color,colorText,spectralSubclass))
            # Gas giants (ORSS)
            numSmallGas = system.TABLE_GAS_GIANT_SMALL[d10]
            numLargeGas = system.TABLE_GAS_GIANT_LARGE[d10]
            # Create list of gas giants
            gasList  = [orbitalobject.Planet(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['SMALL_GAS']) for sg in xrange(numSmallGas)]
            gasList += [orbitalobject.Planet(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['LARGE_GAS']) for lg in xrange(numLargeGas)]
            # Shuffle gas giants into random order
            np.random.shuffle(gasList)
            # Add moons and rings to gas giants. Will replace with main world moons and rings if necessary.
            for gl in gasList:
                # Roll a d20 to determine the number of moons and rings for the giant
                gasD20 = random.dice_roll(1,20)
                # Does the giant have rings
                gl.rings = self.rings(gasD20)
                # Add moons to the gas giant
                gl.moons = self.moons(gasD20)
            # Total number of objects (ORSS)
            numObjects = d4 + d8 - 1
            # Place objects in orbits
            # Create an empty list of orbital objects
            orbitalList = list()
            for o in xrange(numObjects):
                orbitalList.append(None)
            # Check if orbitalList is long enough
            if ( mainOrbit > len(orbitalList) ):
                # Add extra blank spaces if list is not long enough
                for o in xrange(mainOrbit-len(orbitalList)):
                    orbitalList.append(None)
            # Fill main world orbit
            moonList = self.moons(d20)
            #    If airless or thin, determine which one
            if ( mainWorld.atmosphere == world.TABLE_ATMOSPHERE[4] ):
                #    On a d2, 1 is airless, 2 is thin
                #    Airless are going to be space stations or moon bases
                #    Thin are going to be thin atmosphere rocky planets
                if (random.dice_roll(1,2) == 1):
                    # If airless, world is a moon or space station
                    # If main world table rolls has moons, it is a moon, else it is a station
                    if ( len(moonList) > 0 ):
                        isMoon    = True
                        isStation = False
                        # If main world is a moon, is it a moon of a gas giant or rocky world
                        # If the system has gas giants, it is a gas giant moon
                        # Else it is a moon of a rocky planet (should be rare)
                        if ( numSmallGas + numLargeGas > 0):
                            ofGas = True
                        else:
                            ofGas = False
                    else:
                        isMoon    = False
                        isStation = True
                        # If the main world is a space station, is it a space station of a gas giant or rocky world
                        # If the system has gas giants, it is a gas giant station
                        # Else it is a station of a rocky planet (should be rare)
                        if ( numSmallGas + numLargeGas > 0):
                            ofGas = True
                        else:
                            ofGas = False
                else:
                    # Main world is just a thin atmosphere rocky planet
                    isMoon    = False
                    isStation = False
                    ofGas     = False
            else:
                isMoon        = False
                isStation     = False
                ofGas         = False
            # If we just chose a space station for TL2 or lower, turn it into a
            # planet instead. There is no way a TL2- civilization could survive
            # on a space station so we'll remove airless/thin and inert gas
            # atmospheres as options. If a hostile atmoshere still exists, then
            # They'll likely live in the rememants of an underground bunker or 
            # maybe a biodome or something.
            if ( (mainWorld.techLevel == world.TABLE_TECH_LEVEL[2]) or
                 (mainWorld.techLevel == world.TABLE_TECH_LEVEL[3]) or
                 (mainWorld.techLevel == world.TABLE_TECH_LEVEL[4]) ):
                # Planet flags
                isMoon        = False
                isStation     = False
                ofGas         = False
                # New atmosphere roll
                roll2d5 = random.dice_roll(2,5)
                mainWorld.atmosphere = world.TABLE_ALT_ATMOSPHERE[roll2d5]
            # Does it have rings
            hasRings = orbitalobject.TABLE_MINOR_RINGS[d20]
            # Insert main world
            # Moon of another body
            if ( isMoon ):
                # Attach main world to a moon
                moonList[random.dice_roll(1,len(moonList))-1].world = mainWorld
                # Moon of a gas giant
                if ( ofGas ):
                    # Get gas giant to attach world as a moon to
                    gasGiant = gasList.pop(0)
                    # Replace gas giant moon list
                    gasGiant.moons = moonList
                    # Add rings to gas giant if necessary
                    gasGiant.rings = hasRings
                    # Put gas giant into orbit list
                    orbitalList[mainOrbit-1] = gasGiant
                # Moon of a rocky planet
                else:
                    # Create rocky planet
                    rockyPlanet = orbitalobject.Planet(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ROCKY'],
                                                       moons      = moonList,
                                                       rings      = hasRings)
                    # Put rocky planet into orbit list
                    orbitalList[mainOrbit-1] = rockyPlanet
            # Space station around another body
            elif ( isStation ):
                # Create space station and attach world to it
                spaceStation = orbitalobject.SpaceStation(worldObj = mainWorld)
                mainWorld.name += ' Station'
                # Space station around a gas giant
                if ( ofGas ):
                    # Get gas giant to attach world as a space station to
                    gasGiant = gasList.pop(0)
                    # Add world as space station to giant
                    gasGiant.stations.append(spaceStation)
                    # Add main world moons to  gas giant moon list
                    gasGiant.moons += moonList
                    # Add rings to gas giant if necessary
                    gasGiant.rings = hasRings
                    # Put gas giant into orbit list
                    orbitalList[mainOrbit-1] = gasGiant
                # Space station around a rocky planet
                else:
                    # Create rocky planet
                    rockyPlanet = orbitalobject.Planet(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ROCKY'],
                                                       moons      = moonList,
                                                       rings      = hasRings)
                    # Add world as space station to rocky planet
                    rockyPlanet.stations.append(spaceStation)
                    # Replace rocky planet moon list
                    rockyPlanet.moons = moonList
                    # Add rings to rocky planet if necessary
                    rockyPlanet.rings = hasRings
                    # Put gas giant into orbit list
                    orbitalList[mainOrbit-1] = rockyPlanet
            # Rocky world
            else:
                # Create rocky planet
                rockyPlanet = orbitalobject.Planet(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ROCKY'],
                                                   moons      = moonList,
                                                   rings      = hasRings,
                                                   worldObj   = mainWorld)
                orbitalList[mainOrbit-1] = rockyPlanet
            # Asteroid belts (ORSS)
            innerBelts = list()
            for b in xrange(system.TABLE_HYDROCARBON_INNER_ASTEROID_BELTS[d8]):
                innerBelts.append(orbitalobject.AsteroidBelt(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['HYDROCARBON_ASTEROID_BELT']))
            for b in xrange(system.TABLE_ICY_INNER_ASTEROID_BELTS[d8]):
                innerBelts.append(orbitalobject.AsteroidBelt(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ICY_ASTEROID_BELT']))
            for b in xrange(system.TABLE_METALLIC_INNER_ASTEROID_BELTS[d8]):
                innerBelts.append(orbitalobject.AsteroidBelt(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['METALLIC_ASTEROID_BELT']))
            for b in xrange(system.TABLE_ROCKY_INNER_ASTEROID_BELTS[d8]):
                innerBelts.append(orbitalobject.AsteroidBelt(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ROCKY_ASTEROID_BELT']))
            outerBelts = list()
            for b in xrange(system.TABLE_HYDROCARBON_OUTER_ASTEROID_BELTS[d8]):
                outerBelts.append(orbitalobject.AsteroidBelt(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['HYDROCARBON_ASTEROID_BELT']))
            for b in xrange(system.TABLE_ICY_OUTER_ASTEROID_BELTS[d8]):
                outerBelts.append(orbitalobject.AsteroidBelt(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ICY_ASTEROID_BELT']))
            for b in xrange(system.TABLE_METALLIC_OUTER_ASTEROID_BELTS[d8]):
                outerBelts.append(orbitalobject.AsteroidBelt(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['METALLIC_ASTEROID_BELT']))
            for b in xrange(system.TABLE_ROCKY_OUTER_ASTEROID_BELTS[d8]):
                outerBelts.append(orbitalobject.AsteroidBelt(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ROCKY_ASTEROID_BELT']))
            # Insert inner asteroid belts (ORSS)
            for ib in innerBelts:
                # Create inner and outer orbits indices
                innerMin = 0
                innerMax = mainOrbit
                outerMin = mainOrbit+1
                outerMax = len(orbitalList)
                # Try to place in the middle of the inner orbits.
                placed = False
                # If that is full go closer to the main world orbit.
                # If that is full try the beginning of the inner orbits.
                # If that is full place in the first open spot in the outer orbits.
                searchOrder = range(innerMax/2,innerMax) + range(innerMin,innerMax/2) + range(outerMin,outerMax)
                for orbitIndex in searchOrder:
                    # Look for a None slot in the orbitalList to fill
                    if ( orbitalList[orbitIndex] == None ):
                        # Replace None slot with inner belt
                        orbitalList[orbitIndex] = ib
                        placed = True
                        # Stop searching
                        break
                # If there were no slots open, append belt to end of system
                if ( not placed ):
                    orbitalList.append(ib)
            # Insert outer asteroid belts (ORSS)
            for ob in outerBelts:
                # Create outer orbits indices
                outerMin = mainOrbit+1
                outerMax = len(orbitalList)
                # Try to place in the middle of the outer orbits.
                placed = False
                # If that is full go towards the outer orbits
                # If that is full try the beginning of the outer orbits
                searchOrder = range(outerMax/2,outerMax) + range(outerMin,outerMax/2)
                for orbitIndex in searchOrder:
                    # Look for a None slot in the orbitalList to fill
                    if ( orbitalList[orbitIndex] == None ):
                        # Replace None slot with inner belt
                        orbitalList[orbitIndex] = ob
                        placed = True
                        # Stop searching
                        break
                # If there were no slots open, append belt to end of system
                if ( not placed ):
                    orbitalList.append(ob)
            # Create list of worlds still to be placed
            otherAirless = list()
            otherWorlds = list()
            for w in systemObj.worlds:
                # We have already placed the main world
                if ( w is not mainWorld ):
                    # Save airless worlds for later
                    if ( w.atmosphere == world.TABLE_ATMOSPHERE[4] ):
                        # If TL2-, put in other worlds, else put in airless
                        if ( (w.techLevel == world.TABLE_TECH_LEVEL[2]) or
                             (w.techLevel == world.TABLE_TECH_LEVEL[3]) or
                             (w.techLevel == world.TABLE_TECH_LEVEL[4]) ):
                            otherWorlds.append(w)
                        else:
                            # Space stations are cool
                            otherAirless.append(w)
                    else:
                        # Add world to list
                        otherWorlds.append(w)
            ## Place remaining worlds that don't have airless/thin atomspheres
            for ow in otherWorlds:
                # d20 roll for planet stats
                d20 = random.dice_roll(1,20)
                # Create moons
                moonList = self.moons(d20)
                # Create rings
                hasRings = self.rings(d20)
                # Create rocky planet
                rockyPlanet = orbitalobject.Planet(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ROCKY'],
                                                   moons      = moonList,
                                                   rings      = hasRings,
                                                   worldObj   = ow)
                # Planet has not been placed yet
                placed = False
                # If burning start from 1/6 from the innermost orbit
                if ( ow.temperature == world.TABLE_TEMPERATURE[12] ):
                    searchIndex = len(orbitalList)/6
                # If warm start 1/4 from the innermost orbit
                elif ( ow.temperature == world.TABLE_TEMPERATURE[10] ):
                    searchIndex = len(orbitalList)/4
                # If temperate-to-warm start 1/3 from the innermost orbit
                elif ( ow.temperature == world.TABLE_TEMPERATURE[11] ):
                    searchIndex = len(orbitalList)/3
                # If temperate try to put near the middle orbit
                elif ( ow.temperature == world.TABLE_TEMPERATURE[7] ):
                    searchIndex = len(orbitalList)/2
                # If cold to temperate start 2/3 from the innermost orbit
                elif ( ow.temperature == world.TABLE_TEMPERATURE[3] ):
                    searchIndex = 2*len(orbitalList)/3
                # If cold start from 3/4 from the innermost orbit
                elif ( ow.temperature == world.TABLE_TEMPERATURE[4] ):
                    searchIndex = 3*len(orbitalList)/4
                # If frozen start from 5/6 from the innermost orbit
                elif ( ow.temperature == world.TABLE_TEMPERATURE[2] ):
                    searchIndex = 5*len(orbitalList)/6
                # Go outward both directions from starting index
                innerSplit = range(0,searchIndex)[::-1]
                outerSplit = range(searchIndex,len(orbitalList))
                # Create search list from the split lists
                searchList = list()
                for index in xrange(max(len(innerSplit),len(outerSplit))):
                    if ( index < len(innerSplit) ):
                        searchList.append(innerSplit[index])
                    if ( index < len(outerSplit) ):
                        searchList.append(outerSplit[index])
                # Search orbitalList
                for orbitIndex in searchList:
                    # Look for a None slot in the orbital to fill
                    if ( orbitalList[orbitIndex] == None ):
                        # Place rocky planet
                        orbitalList[orbitIndex] = rockyPlanet
                        placed = True
                        # Stop searching
                        break
                # If no open orbit slots, append to end
                if ( not placed ):
                    orbitalList.append(rockyPlanet)
            # Insert gas giants evenly into inner and outer orbits (ORSS)
            for gl in gasList:
                placed = False
                # Get list of indicies of orbits
                orbitIndices = range(len(orbitalList))
                # Shuffle list of indices
                np.random.shuffle(orbitIndices)
                # Search shuffled index list
                for orbitIndex in orbitIndices:
                    # Look for a None slot in the orbital to fill
                    if ( orbitalList[orbitIndex] == None ):
                        # Place rocky planet
                        orbitalList[orbitIndex] = gl
                        placed = True
                        # Stop searching
                        break
                # If no open orbit slots, append to end
                if ( not placed ):
                    orbitalList.append(gl)
            # Insert hot rock, cold stone, and ice planets to fill rest of orbits (ORSS)
            innerOrbits = range(0,mainOrbit)
            for ioIndex in innerOrbits:
                if ( orbitalList[ioIndex] == None ):
                    # d20 roll for planet stats
                    d20 = random.dice_roll(1,20)
                    # Create moons
                    moonList = self.moons(d20)
                    # Create rings
                    hasRings = self.rings(d20)
                    # Create hot planet
                    rockyPlanet = orbitalobject.Planet(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['HOT_ROCK'],
                                                       moons      = moonList,
                                                       rings      = hasRings)
                    # Place planet
                    orbitalList[ioIndex] = rockyPlanet
            outerOrbits = range(mainOrbit,len(orbitalList))
            for ooIndex in outerOrbits:
                if ( orbitalList[ooIndex] == None ):
                    # d20 roll for planet stats
                    d20 = random.dice_roll(1,20)
                    # Create moons
                    moonList = self.moons(d20)
                    # Create rings
                    hasRings = self.rings(d20)
                    # Create cold planet
                    # On a d2, 1 is a cold stone planet and 2 is an ice planet
                    if (random.dice_roll(1,2) == 1):
                        objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['COLD_STONE']
                    else:
                        objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ICE']
                    rockyPlanet = orbitalobject.Planet(objectType = objectType,
                                                       moons      = moonList,
                                                       rings      = hasRings)
                    # Place planet
                    orbitalList[ooIndex] = rockyPlanet
            # Place remaining worlds that have airless/thin atmospheres
            for oa in otherAirless:
                # Planet index to try to place station/base world at
                randomOrbitIndices = range(0,len(orbitalList))
                np.random.shuffle(randomOrbitIndices)
                for roi in randomOrbitIndices:
                    # Avoid asteroid belts
                    if ( not isinstance(orbitalList[roi],orbitalobject.AsteroidBelt) ):
                        # We'll treat all airless/thin as airless at this point to 
                        # offset how we changed the TL2- worlds to something with a 
                        # thicker atmosphere
                        # If 1 it can be a space station
                        # If 2 it can be a moon base if the chosen planet has any moons
                        # otherwise we'll revert to it being a space station
                        isMoon    = False
                        isStation = True
                        if (random.dice_roll(1,2) == 2):
                            if ( len(orbitalList[roi].moons) > 0 ):
                                # If the randomly chosen moon has a world already, just
                                # make this a station instead
                                moonRoll = random.dice_roll(1,len(orbitalList[roi].moons))
                                if ( orbitalList[roi].moons[moonRoll-1].world == None ):
                                    isMoon    = True
                                    isStation = False
                                    moonIndex = moonRoll
                        # Create moon world
                        if ( isMoon ):
                            orbitalList[roi].moons[moonIndex-1].world = oa
                            break
                        # Create space station and attach world to it
                        if ( isStation ):
                            spaceStation = orbitalobject.SpaceStation(worldObj = oa)
                            oa.name += ' Station'
                            break
            # If for some reason a world didn't get put into an orbit, randomly
            # insert it into the orbit list somewhere
            # Get list of worlds in this orbit list
            orbitWorldList = list()
            for ol in orbitalList:
                orbitWorldList += ol.world_list()
            # Compare orbit list worlds system worlds
            for owl in orbitWorldList:
                if ( owl not in systemObj.worlds ):
                    # d20 roll for planet stats
                    d20 = random.dice_roll(1,20)
                    # Create moons
                    moonList = self.moons(d20)
                    # Create rings
                    hasRings = self.rings(d20)
                    # Create rocky planet
                    rockyPlanet = orbitalobject.Planet(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ROCKY'],
                                                       moons      = moonList,
                                                       rings      = hasRings,
                                                       worldObj   = owl)
                    # Randomly place world
                    orbitInsert = random.dice_roll(1,len(orbitalList))-1
                    orbitalList.insert(orbitInsert,rockyPlanet)
            # Put orbital list into system objects list
            systemObj.objects = orbitalList

        # Add corporations -----------------------------------------------------
        for i in xrange(MAX_CORPORATIONS):
            newSector.corporations.append(self.corporation())

        # Add religions --------------------------------------------------------
        for i in xrange(MAX_RELIGIONS):
            newSector.religions.append(self.religion())

        # Return new sector ----------------------------------------------------
        return(newSector)

    def set_seed(self,seedString):
        # Check arguments
        #   name
        seedString = exception.arg_check(seedString,str)
        # Set seed
        random.set_seed(random.seed_alphabet_decode(seedString))
        self.seed = seedString