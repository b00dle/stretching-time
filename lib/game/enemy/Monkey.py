#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
# import BC
from lib.game.enemy.Enemy import Enemy

class Monkey(Enemy):
    ''' Simple enemy using monkey head. '''
    number_of_instances = 0

    def __init__(self):
        self.super(Monkey).__init__()

        self.id = Monkey.number_of_instances
        Monkey.number_of_instances += 1

    def my_constructor(self,
                       PARENT_NODE = None, 
                       SPAWN_TRANSFORM = avango.gua.make_identity_mat()):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        self.geometry = _loader.create_geometry_from_file(
            "monkey_enemy_" + str(Monkey.number_of_instances) + "_geometry",
            "data/objects/monkey.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.geometry.Transform.value = SPAWN_TRANSFORM

        # append to parent
        PARENT_NODE.Children.value.append(self.geometry)