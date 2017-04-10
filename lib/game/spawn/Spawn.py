#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

from lib.game.MovingObject import MovingObject

class Spawn(MovingObject):
    ''' Defines base interface for all Spawn objects in the game. '''

    def __init__(self):
        self.super(Spawn).__init__()

        self.pickable = False