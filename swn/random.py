#!/usr/bin/env python

import numpy as np

SEED_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SEED_ALPHABET_DICT = dict((c, i) for i, c in enumerate(SEED_ALPHABET))
SEED_MAX = 'ZZZZZ'
SEED_MAX_CHAR_LEN = 5 # ZZZZZ is under max uint32, ZZZZZZ is above max uint32

## Dice roll + modifer
#
# Rolls N number of D dice, adding M as a modifier to the result.
# @param num Number of dice to roll.
# @param die Which sided die to roll.
# @param mod Modifier to add to the roll sum result. Default is 0.
def diceRoll(num,die,mod=0):
    return(sum(np.random.random_integers(1,die,num))+mod)

## Random Seed
#
# Randomly selects a seed string and then sets is as the seed.
def randomSeed():
    randomSeedUInt = np.random.random_integers(0,seedAlphabetDecode(SEED_MAX))
    randomSeedString = seedAlphabetEncode(randomSeedUInt)
    setSeed(randomSeedUInt)
    return(randomSeedString)

## Random seed alphabet decode
#
# Decodes a seed into an unsigned integer.
# @param seedString String to be decoded.
def seedAlphabetDecode(seedString):
    # Check length
    if (len(seedString)>SEED_MAX_CHAR_LEN):
        raise(InvalidSeedLengthError("Seed length exceeds max allowed: length %s and max %s" % (len(seedString),SEED_MAX_CHAR_LEN)))
    # Check for invalid characters
    for char in seedString:
        if (char not in SEED_ALPHABET):
            raise(InvalidSeedCharError("Invalid seed character: %s in %s" % (char,seedString)))
    # Convert to uInt
    reverse_base = SEED_ALPHABET_DICT
    length = len(reverse_base)
    ret = 0
    for i, c in enumerate(seedString[::-1]):
        ret += (length ** i) * reverse_base[c]
    return(ret)

## Random seed alphabet encode
#
# Encodes an unsigned integer into the seed alphabet.
# @param seedUInt Integer to be encoded. 
def seedAlphabetEncode(seedUInt):
    if (seedUInt<0):
        raise(InvalidSeedNumberError("Negative number: %i" % seedUInt))
    if (seedUInt>seedAlphabetDecode(SEED_MAX)):
        raise(InvalidSeedNumberError("Seed too large: %i" % seedUInt))
    base=SEED_ALPHABET
    length = len(base)
    ret = ''
    while seedUInt != 0:
        ret = base[seedUInt % length] + ret
        seedUInt /= length
    return(ret)
    
## Set random number generator seed
#
# Set the seed for the numpy random number generator.
# @param seedInt
def setSeed(seedInt):
    np.random.seed(seedInt)

## Invalid seed character exception class.
class InvalidSeedCharError(Exception):
    pass

## Invalid seed length exception class.
class InvalidSeedLengthError(Exception):
    pass

## Invalid seed number exception class.
class InvalidSeedNumberError(Exception):
    pass