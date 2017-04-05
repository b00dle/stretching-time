#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

from lib.game.MovingObject import MovingObject
import lib.game.Globals

class HomingProjectile(MovingObject):
    ''' spawnable object which adjusts moving direction according to target set. '''

    def __init__(self):
        self.super(HomingProjectile).__init__()

        # target node the projectile is aiming for
        self.target = None

        # factor at which movement direction adjustment 
        # is multiplied onto current movement direction
        self.homing_factor = 0.1

        self.target_missed = False

    def my_constructor(self, PARENT_NODE, TARGET, SPAWN_TRANSFORM = avango.gua.make_identity_mat()):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        self.geometry = _loader.create_geometry_from_file(
            "homing_projectile_geometry_GOID_"+str(self.game_object_id),
            "data/objects/cube.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.geometry.Transform.value = SPAWN_TRANSFORM

        self.target = TARGET

        # append to parent
        PARENT_NODE.Children.value.append(self.geometry)

    def evaluate(self):
        ''' BC override. '''
        if self._just_spawned:
            self._just_spawned = False

        if self.target.Parent.value == None:
            self.target_missed = True

        if self.target == None or self.geometry == None:
            print("No target set for HomingProjectile.")
            return

        self._calc_frame_times()
        
        if self.geometry == None:
            return

        self._calc_homing()

        if self.can_move:
            self._move()
        

    def _calc_homing(self):
        ''' adjusts movement dir according to target direction. '''
        target_pos = self.target.WorldTransform.value.get_translate()
        pos = self.geometry.WorldTransform.value.get_translate()

        to_target = target_pos - pos
        to_target.normalize()

        #to_target = to_target * (lib.game.Globals.TIME_FACTOR * self._get_fps_scale() * self.homing_factor) 
        #self.movement_dir = self.movement_dir * (lib.game.Globals.TIME_FACTOR * self._get_fps_scale() * (1 - self.homing_factor)) 
        
        self.movement_dir += to_target * (lib.game.Globals.TIME_FACTOR * self._get_fps_scale() * self.homing_factor)
        self.movement_dir.normalize()

