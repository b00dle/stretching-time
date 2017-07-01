#!/usr/bin/python
# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import random

from lib.game.controller.Spawner import Spawner
from lib.game.spawn.Coin import Coin

class PowerUpSpawner(Spawner):
	''' Manages creation of spawn objects and power ups collectable.
		Also observes position of spawn. If spawn exceeds max bounds,
		it will be removed by the spawner. '''

	def __init__(self):
		self.super(PowerUpSpawner).__init__()

		# vanishing position for spawned objects
		# objects exceeding this plane will be deleted by spawner
		self.z_vanish = 0

		self.max_auto_spawns = 1

	def my_constructor(self, PARENT_NODE = None, AUTO_SPAWN = True, Z_VANISH = 0):
		self.super(PowerUpSpawner).my_constructor(PARENT_NODE, AUTO_SPAWN)

		self.z_vanish = Z_VANISH

	def spawn(self, SPAWN_MIN = avango.gua.Vec3(), SPAWN_MAX = avango.gua.Vec3(), SPAWN_TYPE = 0):
		''' Spawns random spawn at random location. '''
		x = random.uniform(SPAWN_MIN.x, SPAWN_MAX.x)
		y = random.uniform(SPAWN_MIN.y, SPAWN_MAX.y)
		z = random.uniform(SPAWN_MIN.z, SPAWN_MAX.z)

		m = avango.gua.make_trans_mat(x, y, z)

		spawn = Coin()

		spawn.pickable = self.spawn_pickable
		if SPAWN_TYPE == 0:
			tex = 'data/textures/powerups/bomb/bomb_coin_white.png'
			spawn.flags.append('bomb')
		elif SPAWN_TYPE == 1:
			tex = 'data/textures/powerups/cupcakes_decrease/cupcakes_decrease_white.png'
			spawn.flags.append('cup_decrease')
		elif SPAWN_TYPE == 2:
			tex = 'data/textures/powerups/cupcakes_increase/cupcakes_increase_white.png'
			spawn.flags.append('cup_increase')
		elif SPAWN_TYPE == 3:
			tex = 'data/textures/powerups/freeze/freeze_coin_white.png'
			spawn.flags.append('freeze')
		elif SPAWN_TYPE == 4:
			tex = 'data/textures/powerups/godmode/godmode_coin_white.png'
			spawn.flags.append('god')
		elif SPAWN_TYPE == 5:
			tex = 'data/textures/powerups/life/life_coin_white.png'
			spawn.flags.append('life')
		elif SPAWN_TYPE == 6:
			tex = 'data/textures/powerups/normaltime/normaltime_coin_white.png'
			spawn.flags.append('normaltime')
		elif SPAWN_TYPE == 7:
			tex = 'data/textures/powerups/repair/repair_coin_white.png'
			spawn.flags.append('repair')
		elif SPAWN_TYPE == 8:
			tex = 'data/textures/powerups/twice/twice_coin_white.png'
			spawn.flags.append('twice')
		
		spawn.my_constructor(
			PARENT_NODE = self.spawn_root,
			SPAWN_TRANSFORM = m,
			TEXTURE_PATH=tex
		)
		spawn.movement_speed = random.uniform(0.05, 0.15)
		spawn.rotation_speed = 2.0
		spawn.rotation_axis.x = 0.0
		spawn.rotation_axis.y = 1.0
		spawn.rotation_axis.z = 0.0
		spawn.rotation_axis.normalize()
		spawn.setScale(self.spawn_scale)

		self.spawns_dict[spawn.game_object_id] = spawn

	def _remove_vanished(self):
		''' Removes objects moved out of application bounds. '''
		kill_list = []
		for spawn_id in self.spawns_dict:
			spawn = self.spawns_dict[spawn_id]
			z = spawn.bounding_geometry.WorldTransform.value.get_translate().z
			if z > self.z_vanish:
				kill_list.append(spawn_id)

		if len(kill_list) > 0: 
			self.remove_spawns(kill_list)
			
	def _auto_spawn(self):
		''' Spawns one random object inside configured spawn bounds,
			if number of total spawned objects < self.max_auto_spawns. '''
		if self.spawn_count() < self.max_auto_spawns:
			self.spawn(self.auto_spawn_min_pos, self.auto_spawn_max_pos, random.randint(0, 8))