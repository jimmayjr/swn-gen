#!/usr/bin/env python
import functools
import os

_THIS_PATH = os.path.dirname(os.path.realpath(__file__))
_NAME_FILE_PATH = os.path.join(_THIS_PATH,'namefiles')

# Load name files --------------------------------------------------------------
NAMES = dict()
for fName in next(os.walk(_NAME_FILE_PATH))[2]:
    f = open(os.path.join(_NAME_FILE_PATH,fName),'r')
    nameList = []
    for line in f:
        if (line.rstrip() != ''):
            nameList.append(line.rstrip())
    f.close()
    NAMES[fName] = sorted(nameList)

# Sector name file info --------------------------------------------------------
SECTOR_FIRST_NAME_FILES = ['SectorFirst']
sectorFirstNameList = list()
for fName in SECTOR_FIRST_NAME_FILES:
    for name in NAMES[fName]:
        sectorFirstNameList.append(name)

SECTOR_SECOND_NAME_FILES = ['SectorSecond']
sectorSecondNameList = list()
for fName in SECTOR_SECOND_NAME_FILES:
    for name in NAMES[fName]:
        sectorSecondNameList.append(name)

# Star name file info ----------------------------------------------------------
STAR_NAME_FILES = ['AncientGreekFemale',
                   'AncientGreekMale',
                   'ArabicFemale',
                   'ArabicSurname',
                   'BasqueFemale',
                   'HindiFemale',
                   'JapaneseFemale',
                   'JapaneseMale',
                   'ModernGreekSurname',
                   'SpanishSurname',
                   'VikingFemale']
starNameList = list()
for fName in STAR_NAME_FILES:
    for name in NAMES[fName]:
        starNameList.append(name)

# World name file info ---------------------------------------------------------
WORLD_NAME_FILES = ['AncientGreekFemale',
                    'AncientGreekMale',
                    'ArabicFemale',
                    'ArabicSurname',
                    'BasqueFemale',
                    'HindiFemale',
                    'JapaneseFemale',
                    'JapaneseMale',
                    'ModernGreekSurname',
                    'SpanishSurname',
                    'VikingFemale']
worldNameList = list()
for fName in WORLD_NAME_FILES:
    for name in NAMES[fName]:
        worldNameList.append(name)