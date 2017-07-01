#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

from lib.game.misc.TexturedPlane import TexturedPlane

class Ammo(TexturedPlane):
    ''' Ammo styled environment prop. '''

    texture = "data/textures/poempel.png"

    def __init__(self):
        self.super(Ammo).__init__()

    def my_constructor(self, PARENT_NODE, NAME="ammo"):
        self.super(Ammo).my_constructor(PARENT_NODE, Ammo.texture, NAME)
