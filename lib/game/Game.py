#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.controller.Spawner import Spawner
from lib.game.controller.DestructionSpawner import DestructionSpawner
from lib.game.player.Player import Player
from lib.game.tool.SwordDyrion import SwordDyrion
from lib.game.tool.PewPewGun import PewPewGun
from lib.game.tool.HomingGun import HomingGun
import lib.game.Globals

import random

class Game(avango.script.Script):
    ''' Class responsible for managing game logic. '''

    def __init__(self):
        self.super(Game).__init__()

    def my_constructor(self, SCENEGRAPH, HEAD_NODE, SCREEN_NODE, POINTER_INPUT):
        # store scene root
        self.scenegraph = SCENEGRAPH
        self.head_node = HEAD_NODE
        self.screen_node = SCREEN_NODE
        self.pointer_input = POINTER_INPUT
        self.pointer_input.showDebugGeometry(False)

        self._head_pos_buffer = []
        self._velocity_norm = 0.005 # experimentally set 

        self._test()

        # init destruction spawner
        self.destruction_spawner = DestructionSpawner()
        self.destruction_spawner.my_constructor(PARENT_NODE = self.scenegraph.Root.value)

        # init spawner
        self.spawner = Spawner()
        self.spawner.my_constructor(
            PARENT_NODE = self.scenegraph.Root.value,
            Z_VANISH = 2,
            AUTO_SPAWN = True
        )
        self.spawner.auto_spawn_min_pos = avango.gua.Vec3(-1.5, 1.0, -70)
        self.spawner.auto_spawn_max_pos = avango.gua.Vec3(1.5, -1.0, -70)
        self.spawner.max_auto_spawns = 10
        self.spawner.spawn_scale = 0.3
        self.spawner.spawn_pickable = True

        # init player
        p_offset = avango.gua.make_trans_mat(0,0,0.0) * avango.gua.make_scale_mat(0.1,0.1,0.1)
        self.player = Player()
        self.player.my_constructor(PARENT_NODE = self.screen_node, OFFSET_MAT = p_offset)
        
        # init sword tool
        self.dyrion = SwordDyrion()
        self.dyrion.my_constructor(PARENT_NODE = self.player.node, GEOMETRY_SIZE = 0.5)
        self.dyrion.sf_sword_mat.connect_from(self.pointer_input.pointer_node.Transform)
        
        # init gun tool
        '''
        self.pewpew = PewPewGun()
        self.pewpew.my_constructor(
            PARENT_NODE = self.player.node,
            SPAWN_PARENT = self.scenegraph.Root.value,
            GEOMETRY_SIZE = 0.3
        )
        self.pewpew.sf_gun_mat.connect_from(self.pointer_input.pointer_node.Transform)
        self.pewpew.sf_gun_trigger.connect_from(self.pointer_input.sf_button)
        '''

        # init homing gun tool
        self.homing = HomingGun()
        self.homing.my_constructor(
            PARENT_NODE = self.player.node,
            SPAWN_PARENT = self.scenegraph.Root.value,
            TARGET_SPAWNER = self.spawner,
            GEOMETRY_SIZE = 0.3
        )
        self.homing.sf_gun_mat.connect_from(self.pointer_input.pointer_node.Transform)
        self.homing.sf_gun_trigger.connect_from(self.pointer_input.sf_button)
        self.homing.pick_length = 50.0
        self.homing.pick_angle_tolerance = 15.0

        self.always_evaluate(True)

        self._debug_stretch_factor = 2.0

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
        self.player.set_transform(pos)

    def _evaluate_collisions(self):
        ''' evaluates collisions in the game. '''
        player_collide_list = []
        tool_collide_list = []
        for spawn_id in self.spawner.spawns_dict:
            spawn = self.spawner.spawns_dict[spawn_id]
            if not spawn.is_collision_trigger():
                continue
            if self.player.intersects(spawn.get_bounding_box()):
                player_collide_list.append(spawn_id)
            
            if self.dyrion != None and self.dyrion.intersects(spawn.get_bounding_box()):
                tool_collide_list.append(spawn_id)

            if self.homing != None:
                bullet_kill_list = []
                projectile_spawner = self.homing.projectile_spawner
                for bullet_id in projectile_spawner.spawns_dict:
                    bullet = projectile_spawner.spawns_dict[bullet_id]
                    if not bullet.is_collision_trigger():
                        continue
                    for spawn_id in self.spawner.spawns_dict:
                        spawn = self.spawner.spawns_dict[spawn_id]
                        if spawn.is_collision_trigger() and bullet.intersects(spawn.get_bounding_box()):
                            tool_collide_list.append(spawn_id)
                            bullet_kill_list.append(bullet_id)
                if len(bullet_kill_list) > 0:
                    projectile_spawner.remove_spawns(bullet_kill_list)

        player_collide_list = [spawn_id for spawn_id in player_collide_list if spawn_id not in tool_collide_list]
        for spawn_id in player_collide_list:
            spawn = self.spawner.spawns_dict[spawn_id]
            spawn.bounding_geometry.Material.value.set_uniform(
                "Color",
                avango.gua.Vec4(1.0,0.0,0.0,1.0)
            )

        for spawn_id in tool_collide_list:
            spawn = self.spawner.spawns_dict[spawn_id]
            s_pos = spawn.bounding_geometry.WorldTransform.value.get_translate()
            self.destruction_spawner.spawn_destruction(
                SPAWN_POS = s_pos,
                SPAWN_SCALE = 0.05,
                SPAWN_AMOUNT = random.randint(10,20),
                VANISH_DISTANCE = 4.0
            )

        self.spawner.remove_spawns(tool_collide_list)
        