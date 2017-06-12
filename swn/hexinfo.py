#!/usr/bin/env python

import exception
import system

## Hex information base class.
class _HexInfo(object):
    ## Hex information class constructor.
    #  @param self   The object pointer.
    #  @param _name  Information name.
    #  @param _color Information color.
    def __init__(self, _name, _color):
        self._name  = exception.arg_check(_name,  str,         '')
        self._color = exception.arg_check(_color, color.Color, color.NONE)

    def set_name(self, _name):
        self._name  = exception.arg_check(_name, str, '')

    def set_color(self, _color):
        _color = exception.arg_check(_color, color.Color, color.NONE)
        self._color.set_color(_color)

## Hex aggregate information class.
class Hex(object):
    ## Hex data class constructor.
    #  @param self       The object pointer.
    #  @param bgInfo     Background info object.
    #  @param _system    System object.
    #  @param vertexInfo Dictionary of vertex info objects.
    def __init__(self, bgInfo=None, _system=None, vertexInfo=None):
        # Check arguments
        self._bgInfo = exception.arg_check(bgInfo,     HexBackgroundInfo, None)
        self._system = exception.arg_check(_system,    system.System,     None)
        vertexInfo   = exception.arg_check(vertexInfo, dict,              dict())
        # Check vertexInfo argument for invalid vertices or vertex info types
        for vKey in vertexInfo.keys():
            # Do range check on key
            exception.arg_range_check(vKey, 0, 5)
            # Do type check on value
            exception.arg_check(vertexInfo[vKey], HexVertexInfo)
        # Set vertex info data
        self._vertexInfo = vertexInfo

## Hex background information subclass.
class HexBackgroundInfo(_HexInfo):
    ## Hex background information class constructor.
    #  @param self   The object pointer.
    #  @param _name  Information name.
    #  @param _color Information color.
    def __init__(self, _name, _color):
        super(HexBackgroundInfo, self).__init__(_name, _color)

## Hex vertex information subclass.
class HexVertexInfo(_HexInfo):
    ## Hex vertex information class constructor.
    #  @param self   The object pointer.
    #  @param _name  Information name.
    #  @param _color Information color.
    def __init__(self, _name, _color):
        super(HexVertexInfo, self).__init__(_name, _color)