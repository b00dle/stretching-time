#!/usr/bin/python
# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import random
import time

from lib.game.controller.Spawner import Spawner
from lib.game.spawn.Coin import Coin

class ToolSpawner(Spawner):
	''' Manages creation of spawn objects and power ups collectable.
		Also observes position of spawn. If spawn exceeds max bounds,
		it will be removed by the spawner. '''

	def __init__(self):
		self.super(ToolSpawner).__init__()

		# vanishing position for spawned objects
		# objects exceeding this plane will be deleted by spawner
		self.vanish_time = 4.0

		# automatically spawns within given interval
		# unit is seconds
		self.spawn_interval = [5.0, 15.0]

		# states what time to reach to perform auto spawn
		# if number is negative no autospawn will be performed
		self.spawn_at = -1.0

		self.max_auto_spawns = 1

	def my_constructor(self, PARENT_NODE = None, AUTO_SPAWN = True, VANISH_TIME = 3.0):
		self.super(ToolSpawner).my_constructor(PARENT_NODE, AUTO_SPAWN)

		# set members from parameters
		self.vanish_time = VANISH_TIME
		self.auto_spawn = AUTO_SPAWN

	def _remove_vanished(self):
		''' Removes objects timed out by spawner. '''
		current_time = time.time()
		kill_list = []
		for spawn_id in self.spawns_dict:
			spawn = self.spawns_dict[spawn_id]
			if current_time - spawn.get_creation_time() > self.vanish_time:
				kill_list.append(spawn_id)

		if len(kill_list) > 0: 
			self.remove_spawns(kill_list)
		
	def _auto_spawn(self):
		''' Spawns one random object inside configured spawn bounds,
			if number of total spawned objects < self.max_auto_spawns. '''
		current_time = time.time()
		if self.spawn_count() < self.max_auto_spawns:
			if self.spawn_at < 0.0:
				self.spawn_at = time.time() + random.uniform(self.spawn_interval[0], self.spawn_interval[1])
			elif current_time > self.spawn_at:
				_spawn_type = random.randint(0,2)
				self.spawn(self.auto_spawn_min_pos, self.auto_spawn_max_pos, _spawn_type)

	def spawn(self, SPAWN_MIN = avango.gua.Vec3(), SPAWN_MAX = avango.gua.Vec3(), SPAWN_TYPE = 1):
		''' Spawns random spawn at random location. '''
		self.spawn_at = -1.0

		x = random.uniform(SPAWN_MIN.x, SPAWN_MAX.x)
		y = random.uniform(SPAWN_MIN.y, SPAWN_MAX.y)
		z = random.uniform(SPAWN_MIN.z, SPAWN_MAX.z)

		m = avango.gua.make_trans_mat(x, y, z)

		spawn = Coin()

		spawn.pickable = self.spawn_pickable
		if SPAWN_TYPE == 0:
			tex = 'data/textures/sword_psych_stroke.png'
			spawn.flags.append('sword')
		elif SPAWN_TYPE == 1:
			tex = 'data/textures/missile_psych_stroke.png'
			spawn.flags.append('homing')
		elif SPAWN_TYPE == 2:
			tex = 'data/textures/pewpew_coin.png'
			spawn.flags.append('pewpew')
		spawn.my_constructor(
			PARENT_NODE = self.spawn_root,
			SPAWN_TRANSFORM = m,
			TEXTURE_PATH = tex
		)
		spawn.movement_speed = 0.0
		spawn.rotation_speed = 2.0
		spawn.rotation_axis.x = 0.0
		spawn.rotation_axis.y = 1.0
		spawn.rotation_axis.z = 0.0
		spawn.rotation_axis.normalize()
		spawn.setScale(self.spawn_scale)

		self.spawns_dict[spawn.game_object_id] = spawn