#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

from lib.game.misc.TexturedPlane import TexturedPlane

class Heart(TexturedPlane):
    ''' Heart styled environment prop. '''

    alive_texture = "data/textures/heart_noob.png"
    dead_texture = "data/textures/heart_dead.png"

    def __init__(self):
        self.super(Heart).__init__()

        self._is_dead = False

    def my_constructor(self, PARENT_NODE, NAME="heart"):
        self.super(Heart).my_constructor(PARENT_NODE, Heart.alive_texture, NAME)

    def set_dead(self, DEAD=True):
        ''' change texture of heart depending on dead state. '''
        if DEAD != self._is_dead:
            self._is_dead = DEAD
            if self._is_dead:
                self.set_texture(Heart.dead_texture)
            else:
                self.set_texture(Heart.alive_texture)

    def is_dead(self):
        ''' Returns dead state of this instance. '''
        return self._is_dead
