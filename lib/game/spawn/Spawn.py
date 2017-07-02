#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

from lib.game.MovingObject import MovingObject
from lib.game.misc.TexturedPlane import TexturedPlane

class Spawn(MovingObject):
    ''' Defines base interface for all Spawn objects in the game. '''

    def __init__(self):
        self.super(Spawn).__init__()

        self.pickable = False

        self.flags = []

        self.selection_visualizer = None

    def evaluate(self):
        self.super(Spawn).evaluate()
        if self.selection_visualizer != None and self.can_move:
            t = self.bounding_geometry.Transform.value.get_translate()
            s = self.get_scale()
            self.selection_visualizer.node.Transform.value = avango.gua.make_trans_mat(t) * \
                                                             avango.gua.make_scale_mat(s*1.5)

    def my_constructor(self):
        if self.bounding_geometry == None:
            return

        self.selection_visualizer = TexturedPlane()
        self.selection_visualizer.my_constructor(
            PARENT_NODE = self.bounding_geometry.Parent.value,
            TEXTURE_PATH = 'data/textures/selection_visualization.png',
            NAME = 'Spawn_GOID_'+str(self.game_object_id)+'_selection_visualization'
        )
        self.selection_visualizer.node.Transform.value = avango.gua.make_scale_mat(self.get_scale()*1.5)
        self.selection_visualizer.node.Tags.value = ['invisible']

    def cleanup(self):
        self.super(Spawn).cleanup()
        if self.selection_visualizer != None:
            self.selection_visualizer.node.Parent.value.Children.value.remove(self.selection_visualizer.node)
            del self.selection_visualizer
            self.selection_visualizer = None

    def set_selected(self, SELECTED):
        if self.selection_visualizer == None:
            return
        if SELECTED:
            self.selection_visualizer.node.Tags.value = []
        else:
            self.selection_visualizer.node.Tags.value = ['invisible']


