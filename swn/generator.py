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
            # Update count of created systems
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
                numWorlds = system.TABLE_WORLDS[random.diceRoll(1,10)]
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

        # Fill system data -----------------------------------------------------
        # Use one roll star system (ORSS) rules
        for systemKey in newSector.sortedSystems():
            # Get current system
            systemObj = newSector.systems[systemKey]
            # Rolls (ORSS)
            d4  = random.diceRoll(1,4)
            d6  = random.diceRoll(1,6)
            d8  = random.diceRoll(1,8)
            d10 = random.diceRoll(1,10)
            d12 = random.diceRoll(1,12)
            d20 = random.diceRoll(1,20)
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
                d10Mod   = random.diceRoll(1,10)
                # d12 table modifies orbit position (ORSS)
                mainOrbit += system.TABLE_MAIN_WORLD_ORBIT_MOD[d12Mod]
                # Second star color and spectral subclass (ORSS)
                color            = star.TABLE_COLOR[star.TABLE_COLOR_ID[d12Mod]]
                colorText        = star.TABLE_COLOR_TEXT[d12Mod]
                spectralSubclass = star.TABLE_SPECTRAL_SUBCLASS[d10Mod]
                # Add star
                systemObj.stars.append(star.Star(color,colorText,spectralSubclass))
            # Asteroid belts (ORSS)
            numHydrocarbonBelts = system.TABLE_HYDROCARBON_ASTEROID_BELTS[d8]
            numIcyBelts         = system.TABLE_ICY_ASTEROID_BELTS[d8]
            numMetallicBelts    = system.TABLE_METALLIC_ASTEROID_BELTS[d8]
            numRockyBelts       = system.TABLE_ROCKY_ASTEROID_BELTS[d8]
            # Gas giants (ORSS)
            numSmallGas = system.TABLE_GAS_GIANT_SMALL[d10]
            numLargeGas = system.TABLE_GAS_GIANT_LARGE[d10]
            # Create list of gas giants
            gasList  = [orbitalobject.Planet(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['SMALL_GAS']) for sg in xrange(numSmallGas)]
            gasList += [orbitalobject.Planet(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['LARGE_GAS']) for lg in xrange(numLargeGas)]
            np.random.shuffle(gasList)
            # Add moons and rings to gas giants. Will replace with main world moons and rings if necessary.
            for gl in gasList:
                # Roll a d20 to determine the number of moons and rings for the giant
                gasD20 = random.diceRoll(1,20)
                # Number of each type of moon
                numGasSmallMoons  = orbitalobject.TABLE_SMALL_MOONS[gasD20]
                numGasMediumMoons = orbitalobject.TABLE_MEDIUM_MOONS[gasD20]
                # Does the giant have rings
                gl.rings = orbitalobject.TABLE_MINOR_RINGS[gasD20]
                # Create the moons
                gasMoonList  = [orbitalobject.Moon(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['SMALL_MOON']) for sm in xrange(numGasSmallMoons)]
                gasMoonList += [orbitalobject.Moon(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['MEDIUM_MOON']) for mm in xrange(numGasMediumMoons)]
                # Shuffle moons into random order
                np.random.shuffle(gasMoonList)
                # Add moons to the gas giant
                gl.moons = gasMoonList
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
            numMainSmallMoons  = orbitalobject.TABLE_SMALL_MOONS[d20]
            numMainMediumMoons = orbitalobject.TABLE_MEDIUM_MOONS[d20]
            moonList  = [orbitalobject.Moon(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['SMALL_MOON']) for sm in xrange(numMainSmallMoons)]
            moonList += [orbitalobject.Moon(orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['MEDIUM_MOON']) for mm in xrange(numMainMediumMoons)]
            np.random.shuffle(moonList)
            #    If airless or thin, determine which one
            #    On a d2, 1 is airless, 2 is thin
            #    Airless are going to be space stations or moon bases
            #    Thin are going to be thin atmosphere rocky planets
            if (random.diceRoll(1,2) == 1):
                # If airless, world is a moon or space station
                # If main world table rolls has moons, it is a moon, else it is a station
                if ( numMainSmallMoons + numMainMediumMoons > 0 ):
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
            #    Does it have rings
            hasRings = orbitalobject.TABLE_MINOR_RINGS[d20]
            # Insert main world
            # Moon of another body
            if ( isMoon ):
                # Attach main world to a moon
                moonList[random.diceRoll(1,len(moonList))-1].world = mainWorld
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
                spaceStation = orbitalobject.SpaceStation(world = mainWorld)
                # Space station around a gas giant
                if ( ofGas ):
                    # Get gas giant to attach world as a space station to
                    gasGiant = gasList.pop(0)
                    # Add world as space station to giant
                    gasGiant.stations.append(spaceStation)
                    # Replace gas giant moon list
                    gasGiant.moons = moonList
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
                    # Add world as space station to giant
                    rockyPlanet.stations.append(spaceStation)
                    # Replace gas giant moon list
                    rockyPlanet.moons = moonList
                    # Add rings to gas giant if necessary
                    rockyPlanet.rings = hasRings
                    # Put gas giant into orbit list
                    orbitalList[mainOrbit-1] = rockyPlanet
            # Rocky world
            else:
                # Create rocky planet
                rockyPlanet = orbitalobject.Planet(objectType = orbitalobject.TABLE_ORBITAL_OBJECT_TYPE['ROCKY'],
                                                   moons      = moonList,
                                                   rings      = hasRings,
                                                   world      = mainWorld)
                orbitalList[mainOrbit-1] = rockyPlanet
            # Create inner and outer orbits
            innerList = orbitalList[0:mainOrbit]
            outerList = orbitalList[mainOrbit-1:]
            print(len(innerList),len(outerList))
            # Insert asteroid belts
            # Insert gas giants
            # Insert hot rock, cold stone, and ice planets to fill rest of orbits

            # Put orbital list into system objects list
            systemObj.objects = orbitalList

            #orbitalList[mainOrbit-1] = mainWorld

        #for systemKey in newSector.sortedSystems():
        #    systemObj = newSector.systems[systemKey]
        #    for o in systemObj.objects:
        #        if ( o is not None ):
        #            print(o.objectType + ', ',end='')
        #    print('')

            # DEBUG
            #print('Rolls')
            #ollString  =  '{:>2},'.format(d4)
            #rollString += ' {:>2},'.format(d6)
            #rollString += ' {:>2},'.format(d8)
            #rollString += ' {:>2},'.format(d10)
            #rollString += ' {:>2},'.format(d12)
            #rollString += ' {:>2}'.format(d20)
            #print(rollString)
            #print('Modified Rolls')
            #modRollString  =  '{:>2},'.format(d4Mod)
            #modRollString += ' {:>2},'.format('')
            #modRollString += ' {:>2},'.format('')
            #modRollString += ' {:>2},'.format('')
            #modRollString += ' {:>2},'.format('')
            #modRollString += ' {:>2}'.format('')
            #print(modRollString)
            #print(numStars)
            #for (tcKey,tcText) in star.TABLE_COLOR_TEXT.iteritems():
            #    print('{0:>2d}: {1}'.format(tcKey,tcText))
            #for systemKey in newSector.sortedSystems():
            #    if (len(newSector.systems[systemKey].stars)>0):
            #        print(systemKey)
            #        for sta in newSector.systems[systemKey].stars:
            #            print(sta.color,sta.spectralSubclass)

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