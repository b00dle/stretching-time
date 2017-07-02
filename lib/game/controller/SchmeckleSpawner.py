#!/usr/bin/python
# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import random

from lib.game.controller.Spawner import Spawner
from lib.game.spawn.Coin import Coin

class SchmeckleSpawner(Spawner):
	''' Manages creation of spawn objects and power ups collectable.
		Also observes position of spawn. If spawn exceeds max bounds,
		it will be removed by the spawner. '''

	def __init__(self):
		self.super(SchmeckleSpawner).__init__()

		# vanishing position for spawned objects
		# objects exceeding this plane will be deleted by spawner
		self.z_vanish = 0

		self.max_auto_spawns = 3

		# stores metadata for spawn types
		# format (name, file_path, blocked)
		self._spawn_type_info = {
			0 : ['bronze_schmeckle', 'data/textures/shm/bronze_schmeckel_face.png', 18],
			1 : ['silver_schmeckle', 'data/textures/shm/silver_schmeckel_face.png', 11],
			2 : ['gold_schmeckle', 'data/textures/shm/gold_schmeckel_face.png', 3],
		}

	def my_constructor(self, PARENT_NODE = None, AUTO_SPAWN = True, Z_VANISH = 0):
		self.super(SchmeckleSpawner).my_constructor(PARENT_NODE, AUTO_SPAWN)

		self.z_vanish = Z_VANISH

	def spawn(self, SPAWN_MIN = avango.gua.Vec3(), SPAWN_MAX = avango.gua.Vec3(), SPAWN_TYPE = 0):
		''' Spawns random spawn at random location. '''
		x = random.uniform(SPAWN_MIN.x, SPAWN_MAX.x)
		y = random.uniform(SPAWN_MIN.y, SPAWN_MAX.y)
		z = random.uniform(SPAWN_MIN.z, SPAWN_MAX.z)

		m = avango.gua.make_trans_mat(x, y, z)

		spawn = Coin()
		spawn.pickable = self.spawn_pickable

		tex = ''
		if SPAWN_TYPE in self._spawn_type_info:
			tex = self._spawn_type_info[SPAWN_TYPE][1]
			spawn.flags.append(self._spawn_type_info[SPAWN_TYPE][0])
		
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
			type_list = []
			for st in self._spawn_type_info:
				type_list.extend([st for i in range(0, self._spawn_type_info[st][2])])
			spawn_type = type_list[random.randint(0, len(type_list)-1)]
			self.spawn(self.auto_spawn_min_pos, self.auto_spawn_max_pos, spawn_type)