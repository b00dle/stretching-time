#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

import random

# import BC
from lib.game.spawn.Spawn import Spawn

class Plunger(Spawn):
    ''' Simple Spawn using monkey head. TODO setup better bounding box '''
    def __init__(self):
        self.super(Plunger).__init__()

    def my_constructor(self,
                       PARENT_NODE = None, 
                       SPAWN_TRANSFORM = avango.gua.make_identity_mat()):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        loader_flags = avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS
        if self.pickable:
            loader_flags = loader_flags | avango.gua.LoaderFlags.MAKE_PICKABLE

        self.bounding_geometry = _loader.create_geometry_from_file(
            "sphere_spawn_geometry_GOID_"+str(self.game_object_id),
            "data/objects/plunger/plunger_pewpew.obj",
            loader_flags
        )
        self.bounding_geometry.Transform.value = SPAWN_TRANSFORM

        # append to parent
        PARENT_NODE.Children.value.append(self.bounding_geometry)

        # call parent my_constructor
        self.super(Plunger).my_constructor()