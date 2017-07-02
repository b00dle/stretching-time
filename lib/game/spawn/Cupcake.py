#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

import random

# import BC
from lib.game.spawn.Spawn import Spawn

class Cupcake(Spawn):
    ''' Simple Spawn using monkey head. TODO setup better bounding box '''
    def __init__(self):
        self.super(Cupcake).__init__()

    def _get_random_cup_color(self):
        ''' returns a random color for the cup geometry. '''
        _clr_list = [
            avango.gua.Vec4(255.0/256.0, 237.0/256.0, 121.0/256.0, 1.0),
            avango.gua.Vec4(232.0/256.0, 161.0/256.0, 115.0/256.0, 1.0),
            avango.gua.Vec4(255.0/256.0, 136.0/256.0, 223.0/256.0, 1.0),
            avango.gua.Vec4(115.0/256.0, 112.0/256.0, 232.0/256.0, 1.0),
            avango.gua.Vec4(124.0/256.0, 255.0/256.0, 245.0/256.0, 1.0)
        ]
        return _clr_list[random.randint(0, 4)]

    def _get_random_cream_color(self):
        ''' returns a random color for the cream geometry. '''
        _clr_list = [
            avango.gua.Vec4(123.0/256.0, 63.0/256.0, 0.0/256.0, 1.0),
            avango.gua.Vec4(242.0/256.0, 233.0/256.0, 206.0/256.0, 1.0),
            avango.gua.Vec4(255.0/256.0, 252.0/256.0, 251.0/256.0, 1.0),
            avango.gua.Vec4(55.0/256.0, 24.0/256.0, 24.0/256.0, 1.0)
        ]
        return _clr_list[random.randint(0, 3)]

    def _get_random_pastry_color(self):
        ''' returns a random color for the pastry geometry. '''
        _clr_list = [
            avango.gua.Vec4(253.0/256.0, 197.0/256.0, 94.0/256.0, 1.0),
            avango.gua.Vec4(218.0/256.0, 154.0/256.0, 89.0/256.0, 1.0),
            avango.gua.Vec4(140.0/256.0, 86.0/256.0, 55.0/256.0, 1.0),
            avango.gua.Vec4(64.0/256.0, 37.0/256.0, 27.0/256.0, 1.0),
            avango.gua.Vec4(227.0/256.0, 203.0/256.0, 172.0/256.0, 1.0)
        ]
        return _clr_list[random.randint(0, 4)]

    def my_constructor(self,
                       PARENT_NODE = None, 
                       SPAWN_TRANSFORM = avango.gua.make_identity_mat()):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        loader_flags = avango.gua.LoaderFlags.DEFAULTS
        if self.pickable:
            loader_flags = loader_flags | avango.gua.LoaderFlags.MAKE_PICKABLE

        self.bounding_geometry = _loader.create_geometry_from_file(
            "cupcake_spawn_geometry_GOID_"+str(self.game_object_id),
            "data/objects/cube.obj",
            loader_flags
        )
        
        self._transform_node = avango.gua.nodes.TransformNode(
            Name = "cupcake_geometry_transform_GOID_"+str(self.game_object_id)
        )
        self._transform_node.Transform.connect_from(self.bounding_geometry.Transform)

        self.bounding_geometry.Transform.value = SPAWN_TRANSFORM
        self.bounding_geometry.Tags.value = ["invisible"]

        self._cup_geometry = _loader.create_geometry_from_file(
            "cup_GOID_"+str(self.game_object_id),
            "data/objects/cupcake/cupcake_cup.obj",
            loader_flags
        )
        self._cup_geometry.Material.value.set_uniform(
            "Color",
            self._get_random_cup_color()
        )
        self._transform_node.Children.value.append(self._cup_geometry)

        self._pastry_geometry = _loader.create_geometry_from_file(
            "pastry_GOID_"+str(self.game_object_id),
            "data/objects/cupcake/cupcake_pastry.obj",
            loader_flags
        )
        self._pastry_geometry.Material.value.set_uniform(
            "Color",
            self._get_random_pastry_color()
        )
        self._transform_node.Children.value.append(self._pastry_geometry)
        
        self._cream_geometry = _loader.create_geometry_from_file(
            "cream_GOID_"+str(self.game_object_id),
            "data/objects/cupcake/cupcake_cream.obj",
            loader_flags
        )
        self._cream_geometry.Material.value.set_uniform(
            "Color",
            self._get_random_cream_color()
        )
        self._transform_node.Children.value.append(self._cream_geometry)
        
        # append to parent
        PARENT_NODE.Children.value.append(self.bounding_geometry)
        PARENT_NODE.Children.value.append(self._transform_node)

        # call parent my_constructor
        self.super(Cupcake).my_constructor()

    def cleanup(self):
        ''' BC override. '''
        if self._cup_geometry != None:
            self._cup_geometry.Parent.value.Children.value.remove(self._cup_geometry)

        if self._pastry_geometry != None:
            self._pastry_geometry.Parent.value.Children.value.remove(self._pastry_geometry)

        if self._cream_geometry != None:
            self._cream_geometry.Parent.value.Children.value.remove(self._cream_geometry)

        if self._transform_node != None:
            self._transform_node.Transform.disconnect()
            self._transform_node.Parent.value.Children.value.remove(self._transform_node)            

        self.super(Cupcake).cleanup()