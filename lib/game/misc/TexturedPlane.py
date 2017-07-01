#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

class TexturedPlane(avango.script.Script):
    ''' Heart styled environment prop. '''

    def __init__(self):
        self.super(TexturedPlane).__init__()

        # stores root node
        self.node = None

    def my_constructor(self, PARENT_NODE, TEXTURE_PATH, NAME="heart"):
        _loader = avango.gua.nodes.TriMeshLoader() # get trimesh loader to load external meshes

        self.node = _loader.create_geometry_from_file(
            NAME+"_geometry",
            "data/objects/plane.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.node.Material.value.set_uniform("ColorMap", TEXTURE_PATH)

        PARENT_NODE.Children.value.append(self.node)

    def set_texture(self, TEXTURE_PATH):
        if self.node != None:
            self.node.Material.value.set_uniform("ColorMap", TEXTURE_PATH)
