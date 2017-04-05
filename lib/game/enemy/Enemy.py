#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

from lib.game.MovingObject import MovingObject

class Enemy(MovingObject):
    ''' Defines base interface for all enemy objects in the game. '''

    def __init__(self):
        self.super(Enemy).__init__()

        self.pickable = False