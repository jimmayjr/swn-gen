#!/usr/bin/env python

# Functions --------------------------------------------------------------------
## Argument check
def arg_check(arg, argType, argDefault=None):
    # If argType is None, set to default
    if (arg is None):
        return argDefault
    # Else check argument type
    elif (isinstance(arg,argType)):
        return arg
    # Else if wrong type, raise error
    else:
        raise InvalidArgType(arg,argType)

## Range checker
def arg_range_check(arg, low=None, high=None):
    # Check range low if one exists
    if (not (low is None)):
        # Below range
        if (arg < low):
            raise OutsideArgRange(arg,low,high)
    # Check range high if one exists
    if (not (high is None)):
        # Above range
        if (arg > high):
            raise OutsideArgRange(arg,low,high)
    # Return arg
    return arg

# Exceptions -------------------------------------------------------------------
class ExistingDictKey(Exception):
    def __init__(self,key):
        eStringTemplate = 'Key {0} already exists.'
        self.eString = eStringTemplate.format(key)
        Exception.__init__(self,self.eString)

class InvalidArgType(Exception):
    def __init__(self,arg,expectedType):
        eStringTemplate = 'Invalid argument type. Expected \"{1}\" but received \"{0}\".'
        self.eString = eStringTemplate.format(type(arg).__name__,expectedType.__name__)
        Exception.__init__(self,self.eString)

class InvalidListItemType(Exception):
    def __init__(self,item,expectedType):
        eStringTemplate = 'Invalid list item type for. Expected \"{1}\" but received \"{0}\".'
        self.eString = eStringTemplate.format(type(item).__name__,expectedType.__name__)
        Exception.__init__(self,self.eString)

class MaxLoopIterationsExceed(Exception):
    def __init__(self,count):
        eStringTemplate = 'Max number of loop iterations exceeded. Max is {0}.'
        self.eString = eStringTemplate.format(count)
        Exception.__init__(self,self.eString)

class OutsideArgRange(Exception):
    def __init__(self,arg,low,high):
        eStringTemplate = 'Argument outside allowed range. Low: {low}, high: {high}, received: {arg}.'
        self.eString = eStringTemplate.format(low=low, high=high, arg=arg)
        Exception.__init__(self,self.eString)