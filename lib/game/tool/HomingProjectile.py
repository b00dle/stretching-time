#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

import random

from lib.game.MovingObject import MovingObject
import lib.game.Globals

class HomingProjectile(MovingObject):
    ''' spawnable object which adjusts moving direction according to target set. '''

    sf_target_destroyed = avango.SFBool()

    def __init__(self):
        self.super(HomingProjectile).__init__()

        # target node the projectile is aiming for
        self.target = None

        # factor at which movement direction adjustment 
        # is multiplied onto current movement direction
        self.homing_factor = 0.1

        self.target_missed = False

        self.sf_target_destroyed.value = False

        self.node = None

        self._sphere_geometry = None

        self._orbiting_sphere_1 = None
        self._orbiting_sphere_2 = None
        self._orbiting_sphere_3 = None
        self._orbiting_sphere_4 = None

        self._orbit_rotations = []

    def cleanup(self):
        ''' BC override. '''
        self.target = None
        
        if self._orbiting_sphere_1 != None:
            self._orbiting_sphere_1.Parent.value.Children.value.remove(self._orbiting_sphere_1)
        if self._orbiting_sphere_2 != None:
            self._orbiting_sphere_2.Parent.value.Children.value.remove(self._orbiting_sphere_2)
        if self._orbiting_sphere_3 != None:
            self._orbiting_sphere_3.Parent.value.Children.value.remove(self._orbiting_sphere_3)
        if self._orbiting_sphere_4 != None:
            self._orbiting_sphere_4.Parent.value.Children.value.remove(self._orbiting_sphere_4)

        if self.node != None:
            self.node.Transform.disconnect()
            self.node.Parent.value.Children.value.remove(self.node)

        if self._sphere_geometry != None:
            self._sphere_geometry.Parent.value.Children.value.remove(self._sphere_geometry)
        
        self.super(HomingProjectile).cleanup()
        
        self.sf_target_destroyed.disconnect()

    def my_constructor(self, PARENT_NODE, TARGET, SPAWN_TRANSFORM = avango.gua.make_identity_mat()):
        self.target = TARGET
        self.sf_target_destroyed.connect_from(self.target.sf_destroyed)

        # create geometry
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        self.bounding_geometry = _loader.create_geometry_from_file(
            "bounding_geometry_GOID_"+str(self.game_object_id),
            "data/objects/cube.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )

        # add base node for visible geometry transformation
        self.node = avango.gua.nodes.TransformNode(
            Name = "homing_projectile_node_GOID_"+str(self.game_object_id)
        )
        self.node.Transform.connect_from(self.bounding_geometry.Transform)

        self.bounding_geometry.Transform.value = SPAWN_TRANSFORM
        self.bounding_geometry.Tags.value = ["invisible"]

        self._sphere_geometry = _loader.create_geometry_from_file(
            "sphere_geometry_GOID_"+str(self.game_object_id),
            "data/objects/psych_sphere/psych_sphere.obj",
            avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS
        )
        self._sphere_geometry.Transform.value = avango.gua.make_scale_mat(0.7,0.7,0.7) 

        self._orbiting_sphere_1 = _loader.create_geometry_from_file(
            "orbiting_sphere_geometry_1_GOID_"+str(self.game_object_id),
            "data/objects/psych_sphere/psych_sphere.obj",
            avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS
        )
        self._orbiting_sphere_1.Transform.value = avango.gua.make_trans_mat(1.5, 0.0, 0.0) *\
            avango.gua.make_scale_mat(0.5, 0.5, 0.5)

        self._orbiting_sphere_2 = _loader.create_geometry_from_file(
            "orbiting_sphere_geometry_2_GOID_"+str(self.game_object_id),
            "data/objects/psych_sphere/psych_sphere.obj",
            avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS
        )
        self._orbiting_sphere_2.Transform.value = avango.gua.make_trans_mat(0.0, 1.5, 0.0) *\
            avango.gua.make_scale_mat(0.5, 0.5, 0.5)
        
        self._orbiting_sphere_3 = _loader.create_geometry_from_file(
            "orbiting_sphere_geometry_3_GOID_"+str(self.game_object_id),
            "data/objects/psych_sphere/psych_sphere.obj",
            avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS
        )
        self._orbiting_sphere_3.Transform.value = avango.gua.make_trans_mat(-1.5, 0.0, 0.0) *\
            avango.gua.make_scale_mat(0.5, 0.5, 0.5)
        
        self._orbiting_sphere_4 = _loader.create_geometry_from_file(
            "orbiting_sphere_geometry_4_GOID_"+str(self.game_object_id),
            "data/objects/psych_sphere/psych_sphere.obj",
            avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS
        )
        self._orbiting_sphere_4.Transform.value = avango.gua.make_trans_mat(0.0, -1.5, 0.0) *\
            avango.gua.make_scale_mat(0.5, 0.5, 0.5)
        

        # setup orbit rotations
        self._orbit_rotations = [
            avango.gua.Vec4(random.uniform(5.0,7.0), random.uniform(0.0,1.0), random.uniform(0.0,1.0), random.uniform(0.0,1.0)),
            avango.gua.Vec4(random.uniform(5.0,7.0), random.uniform(0.0,1.0), random.uniform(0.0,1.0), random.uniform(0.0,1.0)),
            avango.gua.Vec4(random.uniform(5.0,7.0), random.uniform(0.0,1.0), random.uniform(0.0,1.0), random.uniform(0.0,1.0)),
            avango.gua.Vec4(random.uniform(5.0,7.0), random.uniform(0.0,1.0), random.uniform(0.0,1.0), random.uniform(0.0,1.0))
        ]

        # append to parent
        PARENT_NODE.Children.value.append(self.bounding_geometry)
        PARENT_NODE.Children.value.append(self.node)
        self.node.Children.value.append(self._sphere_geometry)
        self._sphere_geometry.Children.value.append(self._orbiting_sphere_1)
        self._sphere_geometry.Children.value.append(self._orbiting_sphere_2)
        self._sphere_geometry.Children.value.append(self._orbiting_sphere_3)
        self._sphere_geometry.Children.value.append(self._orbiting_sphere_4)

    def evaluate(self):
        ''' BC override. '''
        if self._just_spawned:
            self._just_spawned = False

        if self.target == None or self.bounding_geometry == None:
            #print("no target set for homing projectile")
            return

        self._calc_frame_times()
        
        if self.bounding_geometry == None:
            return

        self._calc_homing()

        if self.can_move:
            self._move()

    def _move(self):
        ''' BC override. '''
        self.super(HomingProjectile)._move()
        
        # move orbiting spheres
        if len(self._orbit_rotations) == 0:
            return

        _s_list = [
            self._orbiting_sphere_1,
            self._orbiting_sphere_2,
            self._orbiting_sphere_3,
            self._orbiting_sphere_4
        ]

        i = 0
        for s in _s_list:
            a = self._orbit_rotations[i].x *\
                lib.game.Globals.TIME_FACTOR *\
                self._get_fps_scale()

            x = self._orbit_rotations[i].y
            y = self._orbit_rotations[i].z
            z = self._orbit_rotations[i].w

            s.Transform.value = avango.gua.make_rot_mat(a, x, y, z) * s.Transform.value
            i += 1

        while len(_s_list) > 0:
            _s_list.pop(0)
        
    def _calc_homing(self):
        ''' adjusts movement dir according to target direction. '''
        target_pos = self.target.bounding_geometry.WorldTransform.value.get_translate()
        pos = self.bounding_geometry.WorldTransform.value.get_translate()

        to_target = target_pos - pos
        to_target.normalize()

        self.movement_dir += to_target * (lib.game.Globals.TIME_FACTOR * self._get_fps_scale() * self.homing_factor)
        self.movement_dir.normalize()

    @field_has_changed(sf_target_destroyed)
    def sf_target_destroyed_has_changed(self):
        if self.sf_target_destroyed.value:
            self.target_missed = True
