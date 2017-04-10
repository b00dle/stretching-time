#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

import random
import math

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

        self._poempel_op = None

    def cleanup(self):
        ''' BC override. '''
        self.target = None
        
        if self._poempel_op != None:
            self._poempel_op.Parent.value.Children.value.remove(self._poempel_op)

        if self.node != None:
            self.node.Transform.disconnect()
            self.node.Parent.value.Children.value.remove(self.node)

        self.super(HomingProjectile).cleanup()
        
        self.sf_target_destroyed.disconnect()

    def my_constructor(self, PARENT_NODE, TARGET, SPAWN_TRANSFORM = avango.gua.make_identity_mat()):
        self.target = TARGET
        self.sf_target_destroyed.connect_from(self.target.sf_destroyed)

        # create geometry
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        self.bounding_geometry = _loader.create_geometry_from_file(
            "homing_projectile_bounding_geometry_GOID_"+str(self.game_object_id),
            "data/objects/cube.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )

        # add base node for visible geometry transformation
        self.node = avango.gua.nodes.TransformNode(
            Name = "homing_projectile_node_GOID_"+str(self.game_object_id)
        )
        self.node.Transform.connect_from(self.bounding_geometry.Transform)

        self._poempel_op = _loader.create_geometry_from_file(
            "homing_poempel_op_geometry_GOID_"+str(self.game_object_id),
            "data/objects/plunger/plunger_homing.obj",
            avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS 
        )

        self.bounding_geometry.Transform.value = SPAWN_TRANSFORM
        self.bounding_geometry.Tags.value = ["invisible"]

        # append to parent
        PARENT_NODE.Children.value.append(self.bounding_geometry)
        PARENT_NODE.Children.value.append(self.node)
        self.node.Children.value.append(self._poempel_op)

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

        if self.can_move:
            self._move()

    def _move(self):
        ''' BC override. '''
        # calculate homing
        target_pos = self.target.bounding_geometry.WorldTransform.value.get_translate()
        pos = self.bounding_geometry.WorldTransform.value.get_translate()

        to_target = target_pos - pos
        to_target.normalize()

        self.movement_dir += to_target * (lib.game.Globals.TIME_FACTOR * self._get_fps_scale() * self.homing_factor)
        self.movement_dir.normalize()

        # calculate to target rotation
        forward = avango.gua.Vec3(0,0,-1)
        axis = forward.cross(to_target)
        axis.normalize()
        angle = math.degrees(math.acos(to_target.dot(forward)))
        rot_mat = avango.gua.make_rot_mat(angle, axis.x, axis.y, axis.z)
        
        # compute translation
        t = self.movement_dir * \
            self.movement_speed * \
            lib.game.Globals.TIME_FACTOR * \
            self._get_fps_scale()
        t += self.bounding_geometry.WorldTransform.value.get_translate()

        s = self.bounding_geometry.WorldTransform.value.get_scale()

        # create transformation matrix (global)
        m = avango.gua.make_trans_mat(t) * \
            avango.gua.make_scale_mat(s) * \
            rot_mat
        
        # apply transformation update (transformation update - local)
        self.bounding_geometry.Transform.value = avango.gua.make_inverse_mat(self.bounding_geometry.Parent.value.WorldTransform.value) * m

    @field_has_changed(sf_target_destroyed)
    def sf_target_destroyed_has_changed(self):
        if self.sf_target_destroyed.value:
            self.target_missed = True
