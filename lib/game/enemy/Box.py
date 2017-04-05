#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
# import BC
from lib.game.enemy.Enemy import Enemy

class Box(Enemy):
    ''' Simple enemy using Box head. '''
    def __init__(self):
        self.super(Box).__init__()

    def my_constructor(self,
                       PARENT_NODE = None, 
                       SPAWN_TRANSFORM = avango.gua.make_identity_mat()):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        loader_flags = avango.gua.LoaderFlags.DEFAULTS
        if self.pickable:
            loader_flags = loader_flags | avango.gua.LoaderFlags.MAKE_PICKABLE

        self.geometry = _loader.create_geometry_from_file(
            "box_enemy_geometry_GOID_"+str(self.game_object_id),
            "data/objects/cube.obj",
            loader_flags 
        )
            
        self.geometry.Transform.value = SPAWN_TRANSFORM

        # append to parent
        PARENT_NODE.Children.value.append(self.geometry)