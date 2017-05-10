#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

class Heart(avango.script.Script):
    ''' Heart styled environment prop. '''

    def __init__(self):
        self.super(Heart).__init__()

        # stores root node
        self.node = None

        self._is_dead = False

    def my_constructor(self, PARENT_NODE, NAME="heart"):
        _loader = avango.gua.nodes.TriMeshLoader() # get trimesh loader to load external meshes

        self.node = _loader.create_geometry_from_file(
            NAME+"_geometry",
            "data/objects/plane.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.node.Material.value.set_uniform("ColorMap", "data/textures/heart_noob.png")

        PARENT_NODE.Children.value.append(self.node)

    def set_dead(self, DEAD=True):
        ''' change texture of heart depending on dead state. '''
        if DEAD != self._is_dead:
            self._is_dead = DEAD
            if self._is_dead:
                self.node.Material.value.set_uniform("ColorMap", "data/textures/heart_dead.png")
            else:
                self.node.Material.value.set_uniform("ColorMap", "data/textures/heart_noob.png")

    def is_dead(self):
        ''' Returns dead state of this instance. '''
        return self._is_dead
