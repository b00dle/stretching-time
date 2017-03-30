#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.controller.Spawner import Spawner
from lib.game.player.Player import Player
import lib.game.Globals

import random

class Game(avango.script.Script):
    ''' Class responsible for managing game logic. '''

    def __init__(self):
        self.super(Game).__init__()

    def my_constructor(self, SCENE_ROOT, HEAD_NODE, SCREEN_NODE):
        # store scene root
        self.scene_root = SCENE_ROOT
        self.head_node = HEAD_NODE
        self.screen_node = SCREEN_NODE

        self._head_pos_buffer = []
        self._velocity_norm = 0.005 # experimentally set 

        self._test()

        # init spawner
        self.spawner = Spawner()
        self.spawner.my_constructor(
            PARENT_NODE = self.scene_root,
            Z_VANISH = 2,
            AUTO_SPAWN = True
        )
        self.spawner.auto_spawn_min_pos = avango.gua.Vec3(-1.5, 1.0, -70)
        #self.spawner.auto_spawn_min_pos = avango.gua.Vec3(0, 0, 0)
        self.spawner.auto_spawn_max_pos = avango.gua.Vec3(1.5, -1.0, -70)
        #self.spawner.auto_spawn_max_pos = avango.gua.Vec3(0, 0, 0)
        self.spawner.max_auto_spawns = 10
        self.spawner.spawn_scale = 0.5

        # init player
        p_offset = avango.gua.make_trans_mat(0,0,0.0) * avango.gua.make_scale_mat(0.1,0.1,0.1)
        self.player = Player()
        self.player.my_constructor(PARENT_NODE = self.screen_node, OFFSET_MAT = p_offset)
        
        self.always_evaluate(True)

        self._debug_stretch_factor = 5.0

    def _test(self):
        ''' debug function for testing purposes. '''
        pass

    def evaluate(self):
        ''' Frame base evaluation function to update game logic. '''
        self._calc_time_stretch()
        self._move_player()
        self._evaluate_collisions()

    def _calc_time_stretch(self):
        ''' calculates a global factor for all time based animations. '''
        head_pos = self.head_node.WorldTransform.value.get_translate()
        self._head_pos_buffer.append(head_pos)
        if len(self._head_pos_buffer) == 10:
            self._head_pos_buffer.pop(0)
        lib.game.Globals.TIME_FACTOR = self._debug_stretch_factor * self._calc_velocity_factor()

    def _calc_velocity_factor(self):
        ''' calculates a velocity value from average movement speed of the head_node. '''
        sum_velocity = sum([(b-a).length() for a,b in zip(self._head_pos_buffer, self._head_pos_buffer[1:])])
        velocity_avg = sum_velocity / len(self._head_pos_buffer)
        return velocity_avg / self._velocity_norm

    def _move_player(self):
        ''' Moves player by offset between this and last frame's head position. '''
        head_m = self.head_node.WorldTransform.value
        pos = head_m.get_translate()
        pos.z = 0.0
        rot = head_m.get_rotate()
        self.player.set_transform(pos, rot)

    def _evaluate_collisions(self):
        ''' evaluates collisions in the game. '''
        kill_list = []
        for spawn_id in self.spawner.spawns_dict:
            spawn = self.spawner.spawns_dict[spawn_id]
            if not spawn.is_collision_trigger():
                continue
            if self.player.intersects(spawn.get_bounding_box()):
                kill_list.append(spawn_id)

        for spawn_id in kill_list:
            spawn = self.spawner.spawns_dict[spawn_id]
            spawn.geometry.Material.value.set_uniform(
                "Color",
                avango.gua.Vec4(1.0,0.0,0.0,1.0)
            )