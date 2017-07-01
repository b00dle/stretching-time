#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
# import BC
from lib.game.spawn.Spawn import Spawn

class Coin(Spawn):
    ''' Simple Spawn using Coin head. '''
    def __init__(self):
        self.super(Coin).__init__()

    def my_constructor(self,
                       PARENT_NODE = None, 
                       SPAWN_TRANSFORM = avango.gua.make_identity_mat(),
                       TEXTURE_PATH = '',
                       COLOR=None):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create bounding_geometry
        loader_flags = avango.gua.LoaderFlags.DEFAULTS
        if self.pickable:
            loader_flags = loader_flags | avango.gua.LoaderFlags.MAKE_PICKABLE

        self.bounding_geometry = _loader.create_geometry_from_file(
            "coin_spawn_bounding_geometry_GOID_"+str(self.game_object_id),
            "data/objects/coin.obj",
            loader_flags 
        )
            
        self.bounding_geometry.Transform.value = SPAWN_TRANSFORM

        if len(TEXTURE_PATH) > 0:
            self.bounding_geometry.Material.value.set_uniform('ColorMap', TEXTURE_PATH)
        elif COLOR != None:
            self.bounding_geometry.Material.value.set_uniform('Color', COLOR)
        else:
            self.bounding_geometry.Material.value.set_uniform('Color', avango.gua.Vec4(0.1, 0.3, 0.65, 1.0))

        # append to parent
        PARENT_NODE.Children.value.append(self.bounding_geometry)