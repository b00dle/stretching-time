#!/usr/bin/python
import avango
import avango.gua
import avango.script

from lib.game.stage.GameStage import GameStage
import lib.game.Globals

import random

class PlayStage(GameStage):
    ''' Encapsulates main gameplay logic. '''

    def __init__(self):
        self.super(PlayStage).__init__()

    def my_constructor(self, GAME):
        self.super(PlayStage).my_constructor(GAME)

    def evaluate_stage(self):
        ''' overrides BC functionality. '''
        if self.is_running():
            self._calc_time_stretch()
            self._evaluate_collisions()
        else:
            print("call start before evaluating stage.")

    def start(self):
        ''' overrides BC functionality. '''
        if self.is_running():
            return
        
        self.super(PlayStage).start()
        
        # configure enemy spawner
        self._game.spawner.auto_spawn = True
        self._game.spawner.auto_spawn_min_pos = avango.gua.Vec3(-1.5, 1.0, -70)
        self._game.spawner.auto_spawn_max_pos = avango.gua.Vec3(1.5, -1.0, -70)
        self._game.spawner.max_auto_spawns = 10
        self._game.spawner.spawn_scale = 0.3
        self._game.spawner.spawn_pickable = True

        # configure tool spawner
        self._game.tool_spawner.auto_spawn = True
        self._game.tool_spawner.auto_spawn_min_pos = avango.gua.Vec3(-1.3, 0.8, 0)
        self._game.tool_spawner.auto_spawn_max_pos = avango.gua.Vec3(1.3, -0.8, 0)
        self._game.tool_spawner.spawn_scale = 0.3
        self._game.tool_spawner.spawn_interval = [0.0, 3.0]

        # configure homing gun
        self._game.homing.sf_gun_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.homing.sf_gun_trigger.connect_from(self._game.pointer_input.sf_button)
        self._game.homing.pick_length = 50.0
        self._game.homing.pick_angle_tolerance = 15.0

        # configure sword
        self._game.dyrion.sf_sword_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_hand_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_grab_trigger.connect_from(self._game.pointer_input.sf_button)

        # show all geometries which should be visible after this stage
        #self._game.dyrion.set_active(True)
        self._game.hand.set_active(True)
        #self._game.homing.set_active(True)

    def stop(self):
        ''' overrides BC functionality. '''
        if not self.is_running():
            return

        self.super(PlayStage).stop()

        # release auto spawn (stop spawning enemies)
        self._game.spawner.auto_spawn = False
        # delete all existing spawns
        kill_list = [key for key in self._game.spawner.spawns_dict.keys()]
        self._game.spawner.remove_spawns(kill_list)

        # release auto spawn (stop spawning tools)
        self._game.tool_spawner.auto_spawn = False
        # delete all existing spawns
        kill_list = [key for key in self._game.tool_spawner.spawns_dict.keys()]
        self._game.tool_spawner.remove_spawns(kill_list)

        ## disconnect connected tool fields
        # homing gun
        self._game.homing.sf_gun_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.homing.sf_gun_trigger.disconnect_from(self._game.pointer_input.sf_button)
        # sword
        self._game.dyrion.sf_sword_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        # hand
        self._game.hand.sf_hand_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_grab_trigger.disconnect_from(self._game.pointer_input.sf_button)
        # hide all geometries which should be invisible after this stage
        #self._game.dyrion.set_active(False)
        self._game.hand.set_active(False)
        #self._game.homing.set_active(False)

    def _calc_time_stretch(self):
        ''' calculates a global factor for all time based animations. '''
        head_pos = self._game.head_node.WorldTransform.value.get_translate()
        self._game.head_pos_buffer.append(head_pos)
        if len(self._game.head_pos_buffer) == 10:
            self._game.head_pos_buffer.pop(0)
        lib.game.Globals.TIME_FACTOR = self._game.debug_stretch_factor * self._calc_velocity_factor()

    def _calc_velocity_factor(self):
        ''' calculates a velocity value from average movement speed of the head_node. '''
        sum_velocity = sum([(b-a).length() for a,b in zip(self._game.head_pos_buffer, self._game.head_pos_buffer[1:])])
        velocity_avg = sum_velocity / len(self._game.head_pos_buffer)
        return velocity_avg / self._game.velocity_norm

    def _evaluate_collisions(self):
        ''' evaluates collisions in the game. '''
        player_collide_list = []
        tool_collide_list = []
        for spawn_id in self._game.spawner.spawns_dict:
            spawn = self._game.spawner.spawns_dict[spawn_id]
            if not spawn.is_collision_trigger():
                continue
            # evaluate collisions with player
            if self._game.player.intersects(spawn.get_bounding_box()):
                player_collide_list.append(spawn_id)
            
            # evaluate collisions with sword
            if self._game.dyrion != None and self._game.dyrion.get_active() and self._game.dyrion.intersects(spawn.get_bounding_box()):
                tool_collide_list.append(spawn_id)

            # evaluate collisions with homing gun 
            if self._game.homing != None and self._game.homing.get_active():
                bullet_kill_list = []
                projectile_spawner = self._game.homing.projectile_spawner
                for bullet_id in projectile_spawner.spawns_dict:
                    bullet = projectile_spawner.spawns_dict[bullet_id]
                    if not bullet.is_collision_trigger():
                        continue
                    for spawn_id in self._game.spawner.spawns_dict:
                        spawn = self._game.spawner.spawns_dict[spawn_id]
                        if spawn.is_collision_trigger() and bullet.intersects(spawn.get_bounding_box()):
                            if spawn_id not in tool_collide_list:
                                tool_collide_list.append(spawn_id)
                            bullet_kill_list.append(bullet_id)
                if len(bullet_kill_list) > 0:
                    projectile_spawner.remove_spawns(bullet_kill_list)
 
        # apply effects of tool collisions
        for spawn_id in tool_collide_list:
            spawn = self._game.spawner.spawns_dict[spawn_id]
            s_pos = spawn.bounding_geometry.WorldTransform.value.get_translate()
            self._game.destruction_spawner.spawn_destruction(
                SPAWN_POS = s_pos,
                SPAWN_SCALE = 0.05,
                SPAWN_AMOUNT = random.randint(10,20),
                VANISH_DISTANCE = 4.0
            )

        self._game.spawner.remove_spawns(tool_collide_list)

        # apply effect of player collisions
        player_collide_list = [spawn_id for spawn_id in player_collide_list if spawn_id not in tool_collide_list]
        if len(player_collide_list) > 0:
            self._game.player.subtract_life()
            self._game.spawner.remove_spawns(player_collide_list)

            if self._game.player.is_dead():
                self._game.end_game(REASON='Player died.')