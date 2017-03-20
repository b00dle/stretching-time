#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
# import BC
from lib.game.enemy.Enemy import Enemy

class Sphere(Enemy):
    ''' Simple enemy using Sphere head. '''
    def __init__(self):
        self.super(Sphere).__init__()

    def my_constructor(self,
                       PARENT_NODE = None, 
                       SPAWN_TRANSFORM = avango.gua.make_identity_mat()):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        self.geometry = _loader.create_geometry_from_file(
            "sphere_enemy_geometry_GOID_"+str(self.get_num_game_objects()),
            "data/objects/sphere.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.geometry.Transform.value = SPAWN_TRANSFORM

        # append to parent
        PARENT_NODE.Children.value.append(self.geometry)