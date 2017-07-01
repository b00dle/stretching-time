#!/usr/bin/python
# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import random

from lib.game.controller.Spawner import Spawner
from lib.game.spawn.Monkey import Monkey
from lib.game.spawn.Sphere import Sphere
from lib.game.spawn.Box import Box
from lib.game.spawn.Cupcake import Cupcake

class EnemySpawner(Spawner):
	''' Manages creation of spawn objects and power ups collectable.
		Also observes position of spawn. If spawn exceeds max bounds,
		it will be removed by the spawner. '''

	def __init__(self):
		self.super(EnemySpawner).__init__()

		# vanishing position for spawned objects
		# objects exceeding this plane will be deleted by spawner
		self.z_vanish = 0

	def my_constructor(self, PARENT_NODE = None, AUTO_SPAWN = True, Z_VANISH = 0):
		self.super(EnemySpawner).my_constructor(PARENT_NODE, AUTO_SPAWN)

		self.z_vanish = Z_VANISH

	def spawn(self, SPAWN_MIN = avango.gua.Vec3(), SPAWN_MAX = avango.gua.Vec3(), SPAWN_TYPE = 3):
		''' Spawns random spawn at random location. '''
		x = random.uniform(SPAWN_MIN.x, SPAWN_MAX.x)
		y = random.uniform(SPAWN_MIN.y, SPAWN_MAX.y)
		z = random.uniform(SPAWN_MIN.z, SPAWN_MAX.z)

		m = avango.gua.make_trans_mat(x, y, z)

		spawn = None
		if SPAWN_TYPE == 0:
			spawn = Monkey()
		elif SPAWN_TYPE == 1:
			spawn = Sphere()
		elif SPAWN_TYPE == 2:
			spawn = Box()
		else:
			spawn = Cupcake()

		spawn.pickable = self.spawn_pickable
		spawn.my_constructor(PARENT_NODE = self.spawn_root, SPAWN_TRANSFORM = m)
		spawn.movement_speed = random.uniform(0.05, 0.15)
		spawn.rotation_speed = random.uniform(0.5,5.0)
		spawn.rotation_axis.x = random.uniform(0.0,1.0)
		spawn.rotation_axis.y = random.uniform(0.0,1.0)
		spawn.rotation_axis.z = random.uniform(0.0,1.0)
		spawn.rotation_axis.normalize()
		spawn.setScale(random.uniform(self.spawn_scale*0.5,self.spawn_scale*1.5))

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
			self.spawn(self.auto_spawn_min_pos, self.auto_spawn_max_pos)