#!/usr/bin/env python

# Argument checker
def ArgCheck(arg,argType,argDefault=None):
    # If argType is None, set to default
    if (arg is None):
        return(argDefault)
    # Else check argument type
    elif (isinstance(arg,argType)):
        return(arg)
    # Else if wrong type, raise error
    else:
        raise InvalidArgType(arg,argType)

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