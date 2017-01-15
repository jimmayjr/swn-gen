#!/usr/bin/env python

import exception
import orbitalobject

# Tables -----------------------------------------------------------------------
# SWN tables
TABLE_ALT_ATMOSPHERE = {
    2:  'Corrosive',
    3:  'Breathable',
    4:  'Breathable',
    5:  'Breathable',
    6:  'Breathable',
    7:  'Breathable',
    8:  'Thick',
    9:  'Invasive, toxic',
    10: 'Corrosive and invasive'
}

TABLE_ATMOSPHERE = {
    2:  'Corrosive',
    3:  'Inert gas',
    4:  'Airless or thin',
    5:  'Breathable',
    6:  'Breathable',
    7:  'Breathable',
    8:  'Breathable',
    9:  'Breathable',
    10: 'Thick',
    11: 'Invasive, toxic',
    12: 'Corrosive and invasive'
}

TABLE_BIOSPHERE = {
    2:  'Remnants',
    3:  'Microbial',
    4:  'No native',
    5:  'No native',
    6:  'Human-miscible',
    7:  'Human-miscible',
    8:  'Human-miscible',
    9:  'Immiscible',
    10: 'Immiscible',
    11: 'Hybrid',
    12: 'Engineered'  
}

TABLE_POPULATION = {
    2:  'Failed colony',
    3:  'Outpost',
    4:  'Tens of thousands',
    5:  'Tens of thousands',
    6:  'Hundreds of thousands',
    7:  'Hundreds of thousands',
    8:  'Hundreds of thousands',
    9:  'Millions',
    10: 'Millions',
    11: 'Billions',
    12: 'Alien civilization'  
}

TABLE_POPULATION_ALT = {
    2:  [         0,          0],
    3:  [       100,       9999],
    4:  [     10000,      99999],
    5:  [     10000,      99999],
    6:  [    100000,     999999],
    7:  [    100000,     999999],
    8:  [    100000,     999999],
    9:  [   1000000,  999999999],
    10: [   1000000,  999999999],
    11: [1000000000,10000000000],
    12: [    100000,   50000000]  
}

TABLE_TAGS = {
    1:  {
        1:  'Abandoned Colony',
        2:  'Alien Ruins',
        3:  'Altered Humanity',
        4:  'Area 51',
        5:  'Badlands World',
        6:  'Bubble Cities',
        7:  'Civil War',
        8:  'Cold War',
        9:  'Colonized Population',
        10: 'Desert World'
    },
    2:  {
        1:  'Eugenic Cult',
        2:  'Exchange Consulate',
        3:  'Feral World',
        4:  'Flying Cities',
        5:  'Forbidden Tech',
        6:  'Freak Geology',
        7:  'Freak Weather',
        8:  'Friendly Foe',
        9:  'Gold Rush',
        10: 'Hatred'
    },
    3:  {
        1:  'Heavy Industry',
        2:  'Heavy Mining',
        3:  'Hostile Biosphere',
        4:  'Hostile Space',
        5:  'Local Specialty',
        6:  'Local Tech',
        7:  'Major Spaceyard',
        8:  'Minimal Contact',
        9:  'Misandry/Misogyny',
        10: 'Ocanic World'
    },
    4:  {
        1:  'Out of Contact',
        2:  'Outpost World',
        3:  'Perimeter Agency',
        4:  'Pilgrimage Site',
        5:  'Police State',
        6:  'Preceptor Archive',
        7:  'Pretech Cultists',
        8:  'Primitive Aliens',
        9:  'Psionics Fear',
        10: 'Psionics Worship'
    },
    5:  {
        1:  'Psionics Academy',
        2:  'Quarantined World',
        3:  'Radioactive World',
        4:  'Regional Hegemon',
        5:  'Restrictive Laws',
        6:  'Rigid Culture',
        7:  'Seagoing Cities',
        8:  'Sealed Menace',
        9:  'Sectarians',
        10: 'Seismic Instability'
    },
    6:  {
        1:  'Secret Masters',
        2:  'Theocracy',
        3:  'Tomb World',
        4:  'Trade Hub',
        5:  'Tyranny',
        6:  'Unbraked AI',
        7:  'Warlords',
        8:  'Xenophiles',
        9:  'Xenophobes',
        10: 'Zombies'
    }

}

TABLE_TECH_LEVEL = {
    2:  '0',
    3:  '1',
    4:  '2',
    5:  '3',
    6:  '3',
    7:  '4',
    8:  '4',
    9:  '4',
    10: '4',
    11: '4+',
    12: '5' 
}

TABLE_TECH_LEVEL_REVERSE = {
    '0':  0,
    '1':  1,
    '2':  2,
    '3':  3,
    '4':  4,
    '4+': 5,
    '5':  6
}

TABLE_TEMPERATURE = {
    2:  'Frozen',
    3:  'Cold-to-temperate',
    4:  'Cold',
    5:  'Cold',
    6:  'Temperate',
    7:  'Temperate',
    8:  'Temperate',
    9:  'Warm',
    10: 'Warm',
    11: 'Temperate-to-warm',
    12: 'Burning'
}

# One Roll Star System tables
TABLE_MAIN_WORLD_ORBIT_TEMP_MOD = {
    'Frozen':             2,
    'Cold-to-temperate':  1,
    'Cold':               1,
    'Cold':               1,
    'Temperate':          0,
    'Temperate':          0,
    'Temperate':          0,
    'Warm':              -1,
    'Warm':              -1,
    'Temperate-to-warm':  0,
    'Burning':           -2
}

# World class ------------------------------------------------------------------
class World(object):
    def __init__(self,
                 name = '',
                 atmosphere = '',
                 biosphere = '',
                 population = '',
                 populationAlt = 0,
                 tags = ['',''],
                 temperature = '',
                 techLevel = '0'):
        # General information
        self.name = exception.arg_check(name,str,'')

        # Roll information
        self.atmosphere  = exception.arg_check(atmosphere,str,'')
        self.biosphere   = exception.arg_check(biosphere,str,'')
        self.population  = exception.arg_check(population,str,'')
        self.tags        = exception.arg_check(tags,list,['',''])
        for tag in tags:
            if not (isinstance(tag,str)):
                raise exception.InvalidListItemType(tag,str)
        self.temperature = exception.arg_check(temperature,str,'')
        self.techLevel   = exception.arg_check(techLevel,str,'0')

        # Alternate roll information
        self.populationAlt = exception.arg_check(populationAlt,int,0)

    def population_alt_text(self):
        # Floor to 3 significant figures
        if ( self.populationAlt > 99999 ):
            return('{:,}'.format(int(str(self.populationAlt)[0:3]+'0'*(len(str(self.populationAlt))-3))))
        # Floor to nearest 1000
        elif ( self.populationAlt > 9999 ):
            return('{:,}'.format(int(str(self.populationAlt)[0:2]+'0'*(len(str(self.populationAlt))-2))))
        # Floor to nearest 100
        elif ( self.populationAlt > 999 ):
            return('{:,}'.format(int(str(self.populationAlt)[0:2]+'0'*(len(str(self.populationAlt))-2))))
        # Floor to nearest 10
        elif ( self.populationAlt > 99 ):
            return(str(self.populationAlt)[0:1]+'0'*(len(str(self.populationAlt))-1))
        # Else just return value
        else:
            return(str(self.populationAlt))
