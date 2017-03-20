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

    def my_constructor(self, SCENE_ROOT):
        # store scene root
        self.scene_root = SCENE_ROOT
        self._test()

        # init spawner
        self.spawner = Spawner()
        self.spawner.my_constructor(
            PARENT_NODE = self.scene_root,
            Z_VANISH = 0.25,
            AUTO_SPAWN = True
        )
        self.spawner.auto_spawn_min_pos = avango.gua.Vec3(-10, -8, 0)
        #self.spawner.auto_spawn_min_pos = avango.gua.Vec3(0, 0, 0)
        self.spawner.auto_spawn_max_pos = avango.gua.Vec3(10, 8, 0)
        #self.spawner.auto_spawn_max_pos = avango.gua.Vec3(0, 0, 0)
        self.spawner.max_auto_spawns = 10

        # init player
        p_offset = avango.gua.make_trans_mat(0,0,0.2) * avango.gua.make_scale_mat(0.01,0.01,0.01)
        self.player = Player()
        self.player.my_constructor(PARENT_NODE = self.scene_root, OFFSET_MAT = p_offset)
        
        self.always_evaluate(True)

        self._debug_stretch_factor = 1.0

    def _test(self):
        ''' debug function for testing purposes. '''
        pass

    def evaluate(self):
        ''' Frame base evaluation function to update game logic. '''
        self._calc_time_stretch()
        self._evaluate_collisions()

    def _calc_time_stretch(self):
        ''' calculates a global factor for all time based animations. '''
        lib.game.Globals.TIME_FACTOR += self._debug_stretch_factor * 0.01
        if lib.game.Globals.TIME_FACTOR > 1.5:
            self._debug_stretch_factor = -1.0
        elif lib.game.Globals.TIME_FACTOR < 0.5:
            self._debug_stretch_factor = 1.0

    def _evaluate_collisions(self):
        ''' evaluates collisions in the game. '''
        kill_list = []
        for spawn in self.spawner.spawns:
            if not spawn.is_collision_trigger():
                continue
            if self.player.intersects(spawn.get_bounding_box()):  
                kill_list.append(spawn)
        if len(kill_list) > 0:
            self.spawner.remove_spawns(kill_list)