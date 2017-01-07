#!/usr/bin/env python

# Tables -----------------------------------------------------------------------
TABLE_EVOLUTION = {
    1: 'New holy book',
    2: 'New prophet',
    3: 'Syncretism',
    4: 'Neofundamentalism',
    5: 'Quietism',
    6: 'Sacrifices',
    7: 'Schism',
    8: 'Holy family'
}

TABLE_LEADERSHIP = {
    1: 'Patriarch/Matriarch',
    2: 'Patriarch/Matriarch',
    3: 'Council',
    4: 'Council',
    5: 'Democracy',
    6: 'No universal leadership'
}

TABLE_ORIGIN_TRADITION = {
    1:  'Paganism',
    2:  'Roman Catholicism',
    3:  'Eastern Orthodox Christianity',
    4:  'Protestant Christianity',
    5:  'Buddhism',
    6:  'Judaism',
    7:  'Islam',
    8:  'Taoism',
    9:  'Hinduism',
    10: 'Zoroastrianism',
    11: 'Confucianism',
    12: 'Ideology',
}

# Religion class ---------------------------------------------------------------
class Religion(object):
    def __init__(self,
                 evolution  = '',
                 leadership = '',
                 origin     = ''):
        self.evolution  = evolution
        self.leadership = leadership
        self.origin     = origin