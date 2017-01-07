#!/usr/bin/env python

import abc

# Base Planet class ------------------------------------------------------------
class BasePlanet(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def __init__(self):
        pass