#!/usr/bin/python
import avango
import avango.gua
import avango.script

from lib.game.stage.GameStage import GameStage
import lib.game.Globals

import random
import time

class PlayStage(GameStage):
    ''' Encapsulates main gameplay logic. '''

    score_values = {
        'cup_kill' : 666,
        'tool_collect' : 123,
        'powerup_collect' : 420,
        'cup_avoid' : 66,
        'bronze_schmeckle' : 240,
        'silver_schmeckle' : 483,
        'gold_schmeckle' : 805
    }

    def __init__(self):
        self.super(PlayStage).__init__()

        self.removed_cupcakes = 0
        self._powerup_clocks = {
            'freeze' : -1.0,
            'god' : -1.0,
            'normaltime' : -1.0,
            'twice' : -1.0
        }
        self._last_frame_time = time.time()

    def my_constructor(self, GAME):
        self.super(PlayStage).my_constructor(GAME)

    def evaluate_stage(self):
        ''' overrides BC functionality. '''
        if self.is_running():
            self._calc_time_stretch()
            if self._game.hand.get_active():
                self._evaluate_tool_pick()
            else:
                self._evaluate_tool_decay()
            self._evaluate_enemy_collision()
            self._evaluate_powerups()
            self._evaluate_schmeckles()
            self._evaluate_misc_scores()
        else:
            print("call start before evaluating stage.")#
        self._last_frame_time = time.time()

    def start(self):
        ''' overrides BC functionality. '''
        if self.is_running():
            return
        
        self.super(PlayStage).start()
        
        self.removed_cupcakes = 0

        # configure enemy spawner
        self._game.spawner.auto_spawn = True
        self._game.spawner.auto_spawn_min_pos = avango.gua.Vec3(-1.5, 1.0, -70)
        self._game.spawner.auto_spawn_max_pos = avango.gua.Vec3(1.5, -1.0, -70)
        self._game.spawner.max_auto_spawns = 10
        self._game.spawner.spawn_scale = 0.3
        self._game.spawner.spawn_pickable = True

        # configure powerup spawner
        self._game.powerup_spawner.auto_spawn = True
        self._game.powerup_spawner.auto_spawn_min_pos = avango.gua.Vec3(-1.5, 1.0, -70)
        self._game.powerup_spawner.auto_spawn_max_pos = avango.gua.Vec3(1.5, -1.0, -70)
        self._game.powerup_spawner.max_auto_spawns = 1
        self._game.powerup_spawner.spawn_scale = 0.5
        self._game.powerup_spawner.spawn_pickable = True
        self._game.powerup_spawner.set_spawn_type_block('repair', True)
        self._game.powerup_spawner.set_spawn_type_block('life', True)

        # configure powerup spawner
        self._game.schmeckle_spawner.auto_spawn = True
        self._game.schmeckle_spawner.auto_spawn_min_pos = avango.gua.Vec3(-1.5, 1.0, -70)
        self._game.schmeckle_spawner.auto_spawn_max_pos = avango.gua.Vec3(1.5, -1.0, -70)
        self._game.schmeckle_spawner.max_auto_spawns = 3
        self._game.schmeckle_spawner.spawn_scale = 0.5
        self._game.schmeckle_spawner.spawn_pickable = True

        # configure tool spawner
        self._game.tool_spawner.auto_spawn = True
        self._game.tool_spawner.auto_spawn_min_pos = avango.gua.Vec3(-1.3, 0.8, -0.5)
        self._game.tool_spawner.auto_spawn_max_pos = avango.gua.Vec3(1.3, -0.8, -0.5)
        self._game.tool_spawner.spawn_scale = 0.15
        self._game.tool_spawner.spawn_interval = [0.0, 5.0]
        self._game.tool_spawner.vanish_time = 5.0
        self._game.tool_spawner.max_auto_spawns = 1

        # configure homing gun
        self._game.homing.sf_gun_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.homing.sf_gun_trigger.connect_from(self._game.pointer_input.sf_button)
        self._game.homing.pick_length = 50.0
        self._game.homing.pick_angle_tolerance = 15.0

        # configure pew pew gun
        self._game.pewpew.sf_gun_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.pewpew.sf_gun_trigger.connect_from(self._game.pointer_input.sf_button)
        
        # configure sword
        self._game.dyrion.sf_sword_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_hand_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_grab_trigger.connect_from(self._game.pointer_input.sf_button)

        # show all geometries which should be visible after this stage
        self._game.hand.set_active(True)
        self._game.dyrion.set_active(False)
        self._game.homing.set_active(False)
        self._game.pewpew.set_active(False)

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

        # release auto spawn (stop spawning powerups)
        self._game.powerup_spawner.auto_spawn = False
        # delete all existing powerup spawns
        kill_list = [key for key in self._game.powerup_spawner.spawns_dict.keys()]
        self._game.powerup_spawner.remove_spawns(kill_list)
        self._game.powerup_spawner.set_spawn_type_block('repair', True)
        self._game.powerup_spawner.set_spawn_type_block('life', True)

        # release auto spawn (stop spawning schmeckles)
        self._game.schmeckle_spawner.auto_spawn = False
        # delete all existing powerup spawns
        kill_list = [key for key in self._game.schmeckle_spawner.spawns_dict.keys()]
        self._game.schmeckle_spawner.remove_spawns(kill_list)

        # release auto spawn (stop spawning tools)
        self._game.tool_spawner.auto_spawn = False
        # delete all existing spawns
        kill_list = [key for key in self._game.tool_spawner.spawns_dict.keys()]
        self._game.tool_spawner.remove_spawns(kill_list)

        ## disconnect connected tool fields
        # homing gun
        self._game.homing.sf_gun_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.homing.sf_gun_trigger.disconnect_from(self._game.pointer_input.sf_button)
        # pewpew gun
        self._game.pewpew.sf_gun_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.pewpew.sf_gun_trigger.disconnect_from(self._game.pointer_input.sf_button)
        # sword
        self._game.dyrion.sf_sword_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        # hand
        self._game.hand.sf_hand_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_grab_trigger.disconnect_from(self._game.pointer_input.sf_button)
        # hide all geometries which should be invisible after this stage
        self._game.dyrion.set_active(False)
        self._game.hand.set_active(False)
        self._game.homing.set_active(False)
        self._game.pewpew.set_active(False)

        while self._game.player.subtract_ammo():
            pass

    def _calc_time_stretch(self):
        ''' calculates a global factor for all time based animations. '''
        head_pos = self._game.head_node.WorldTransform.value.get_translate()
        self._game.head_pos_buffer.append(head_pos)
        if len(self._game.head_pos_buffer) == 10:
            self._game.head_pos_buffer.pop(0)
        lib.game.Globals.TIME_FACTOR = self._game.debug_stretch_factor * self._calc_velocity_factor()

    def _calc_velocity_factor(self):
        ''' calculates a velocity value from average movement speed of the head_node. '''
        if self._powerup_clocks['freeze'] > 0.0:
            return 0.0
        if self._powerup_clocks['normaltime'] > 0.0:
            return 1.0
        sum_velocity = sum([(b-a).length() for a,b in zip(self._game.head_pos_buffer, self._game.head_pos_buffer[1:])])
        velocity_avg = sum_velocity / len(self._game.head_pos_buffer)
        return velocity_avg / self._game.velocity_norm

    def _enable_tool(self, TOOL):
        self._game.hand.set_active(False)
        self._game.tool_spawner.auto_spawn = False
        TOOL.set_active(True)
        TOOL.use_count = 0
        self._game.tool_spawner.remove_spawn(self._game.hand.pick_result)
        self._game.player.add_ammo(COUNT=TOOL.max_use)
        self._game.powerup_spawner.set_spawn_type_block('repair', False)
        self._score('tool_collect')

    def _disable_tool(self, TOOL):
        TOOL.set_active(False)
        self._game.hand.set_active(True)
        self._game.tool_spawner.auto_spawn = True
        self._game.powerup_spawner.set_spawn_type_block('repair', True)

    def _evaluate_tool_pick(self):
        ''' calculates selection of a tool. '''
        if self._game.hand.pick_result != None and self._game.hand.pick_result in self._game.tool_spawner.spawns_dict:
            picked_tool = self._game.tool_spawner.spawns_dict[self._game.hand.pick_result]
            if 'sword' in picked_tool.flags:
                picked_tool = None
                self._enable_tool(TOOL=self._game.dyrion)
            elif 'homing' in picked_tool.flags:
                picked_tool = None
                self._enable_tool(TOOL=self._game.homing)
            elif 'pewpew' in picked_tool.flags:
                picked_tool = None
                self._enable_tool(TOOL=self._game.pewpew)

    def _evaluate_tool_decay(self):
        tools = [self._game.dyrion, self._game.homing, self._game.pewpew]
        for tool in tools:
            if tool.get_active():
                if tool.is_used_up():
                    self._disable_tool(tool)
                self._evaluate_player_ammo(tool)

    def _evaluate_player_ammo(self, TOOL):
        left = TOOL.max_use - TOOL.use_count
        diff = left - self._game.player.get_ammo()
        if diff == 0:
            return

        add = diff > 0
        for i in range(0, abs(diff)):
            if add:
                self._game.player.add_ammo()
            else:
                self._game.player.subtract_ammo()

    def _evaluate_enemy_collision(self):
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
                self._game.dyrion.use_count += 1

            # evaluate collisions with homing gun 
            if self._game.homing != None:
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

            # evaluate collisions with pewpew gun 
            if self._game.pewpew != None:
                bullet_kill_list = []
                projectile_spawner = self._game.pewpew.projectile_spawner
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
            self._score(WHAT='cup_kill')
            self.removed_cupcakes += 1

        self._game.spawner.remove_spawns(tool_collide_list)

        # apply effect of player collisions
        player_collide_list = [spawn_id for spawn_id in player_collide_list if spawn_id not in tool_collide_list]
        if len(player_collide_list) > 0:
            if not self._powerup_clocks['god'] > 0.0:
                self._game.player.subtract_life()
                if self._game.powerup_spawner.get_spawn_type_block('life'):
                    self._game.powerup_spawner.set_spawn_type_block('life', False)
            self._game.spawner.remove_spawns(player_collide_list)

            if self._game.player.is_dead():
                self._game.end_game(REASON='Player died.')

    def _evaluate_powerups(self):
        collected_power_ups = {}
        for spawn_id in self._game.powerup_spawner.spawns_dict:
            spawn = self._game.powerup_spawner.spawns_dict[spawn_id]
            if not spawn.is_collision_trigger():
                continue

            # evaluate collisions with player
            if self._game.player.intersects(spawn.get_bounding_box()):
                collected_power_ups[spawn_id] = spawn.flags
            else:
                active_tool = self._get_active_tool()
                if active_tool != None and active_tool.intersects(spawn.get_bounding_box()):
                    collected_power_ups[spawn_id] = spawn.flags

        if len(collected_power_ups) > 0:
            self._apply_powerups(collected_power_ups)
            self._game.powerup_spawner.remove_spawns(collected_power_ups.keys())

        elapsed = time.time() - self._last_frame_time
        for clock in self._powerup_clocks:
            if self._powerup_clocks[clock] > 0.0:
                self._powerup_clocks[clock] -= elapsed
                if self._powerup_clocks[clock] < 0.0:
                    self._powerup_clocks[clock] = -1.0
                    if clock == 'freeze':
                        self._game.freeze_coin.show_secondary_texture(False)
                    elif clock == 'god':
                        self._game.god_coin.show_secondary_texture(False)
                    elif clock == 'normaltime':
                        self._game.normaltime_coin.show_secondary_texture(False)
                    elif clock == 'twice':
                        self._game.twice_coin.show_secondary_texture(False)


    def _get_active_tool(self):
        for tool in [self._game.hand, self._game.homing, self._game.dyrion, self._game.pewpew]:
            if tool.get_active():
                return tool

    def _apply_powerups(self, POWERUPS):
        for goid in POWERUPS:
            if 'bomb' in POWERUPS[goid]:
                self._powerup_bomb()
            elif 'cup_decrease' in POWERUPS[goid]:
                self._powerup_decrease()
            elif 'cup_increase' in POWERUPS[goid]:
                self._powerup_increase()
            elif 'freeze' in POWERUPS[goid]:
                self._increase_powerup_clock('freeze', 5)
            elif 'god' in POWERUPS[goid]:
                self._increase_powerup_clock('god', 10)
            elif 'life' in POWERUPS[goid]:
                self._powerup_life()
            elif 'normaltime' in POWERUPS[goid]:
                self._increase_powerup_clock('normaltime', 10)
            elif 'repair' in POWERUPS[goid]:
                self._powerup_repair()
            elif 'twice' in POWERUPS[goid]:
                self._increase_powerup_clock('twice', 15)
            self._score('powerup_collect')

    def _powerup_bomb(self):
        ''' destroys all currently visible spawned cupcakes. '''
        all_spawns = [k for k in self._game.spawner.spawns_dict.keys()]
        # apply effects of tool collisions
        for spawn_id in all_spawns:
            spawn = self._game.spawner.spawns_dict[spawn_id]
            s_pos = spawn.bounding_geometry.WorldTransform.value.get_translate()
            self._game.destruction_spawner.spawn_destruction(
                SPAWN_POS = s_pos,
                SPAWN_SCALE = 0.05,
                SPAWN_AMOUNT = random.randint(10,20),
                VANISH_DISTANCE = 4.0
            )

        self._game.spawner.remove_spawns(all_spawns)

    def _powerup_decrease(self):
        ''' halfes the size of all cupcakes. '''
        for spawn in self._game.spawner.spawns_dict.values():
            s = spawn.get_scale()
            spawn.setScale(s.x*0.5)

    def _powerup_increase(self):
        ''' halfes the size of all cupcakes. '''
        for spawn in self._game.spawner.spawns_dict.values():
            s = spawn.get_scale()
            spawn.setScale(s.x*2.0)

    def _powerup_repair(self):
        ''' fills up ammo for current tool. '''
        if self._game.hand.get_active():
            return
        if self._game.dyrion.get_active():
            self._game.dyrion.use_count = 0
            self._game.player.add_ammo(self._game.dyrion.max_use - self._game.player.get_ammo())

    def _powerup_life(self):
        self._game.player.add_life()
        if self._game.player.has_max_life():
            self._game.powerup_spawner.set_spawn_type_block('life', True)

    def _increase_powerup_clock(self, CLOCK, SECONDS):
        if self._powerup_clocks[CLOCK] < 0.0:
            self._powerup_clocks[CLOCK] = SECONDS
        else:
            self._powerup_clocks[CLOCK] += SECONDS 

        if CLOCK == 'freeze':
            self._game.freeze_coin.show_secondary_texture()
        elif CLOCK == 'god':
            self._game.god_coin.show_secondary_texture()
        elif CLOCK == 'normaltime':
            self._game.normaltime_coin.show_secondary_texture()
        elif CLOCK == 'twice':
            self._game.twice_coin.show_secondary_texture()

    def _evaluate_schmeckles(self):
        collected_schmeckles = {}
        for spawn_id in self._game.schmeckle_spawner.spawns_dict:
            spawn = self._game.schmeckle_spawner.spawns_dict[spawn_id]
            if not spawn.is_collision_trigger():
                continue
            # evaluate collisions with player
            if self._game.player.intersects(spawn.get_bounding_box()):
                collected_schmeckles[spawn_id] = spawn.flags
            else:
                active_tool = self._get_active_tool()
                if active_tool != None and active_tool.intersects(spawn.get_bounding_box()):
                    collected_schmeckles[spawn_id] = spawn.flags
        
        if len(collected_schmeckles) > 0:
            self._apply_schmeckle_scores(collected_schmeckles)
            self._game.schmeckle_spawner.remove_spawns(collected_schmeckles.keys())

    def _apply_schmeckle_scores(self, SCHMECKLES):
        for shm in SCHMECKLES.values():
            for value in shm:
                self._score(value)

    def _evaluate_misc_scores(self):
        if self._game.spawner.removed_spawns > self.removed_cupcakes:
            diff = self._game.spawner.removed_spawns - self.removed_cupcakes
            self._score(WHAT='cup_avoid', COUNT=diff)
            self.removed_cupcakes = self._game.spawner.removed_spawns

    def _score(self, WHAT, COUNT=1):
        ''' score points in game. PlayStage.score_values offers dict into what can be scored
            and what the default point score will be. 
            All default scores will be factored with the current lib.game.Globals.TIME_FACTOR.
            COUNT specifies how often the final score should be added to the total score. '''
        if WHAT not in PlayStage.score_values:
            return
        for i in range(0, COUNT):
            twice = 1.0
            if self._powerup_clocks['twice']:
                twice = 2.0
            self._game.add_game_score(twice*lib.game.Globals.TIME_FACTOR*PlayStage.score_values[WHAT])
