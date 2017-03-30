#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import random

from lib.game.enemy.Monkey import Monkey
from lib.game.enemy.Sphere import Sphere
from lib.game.enemy.Box import Box

class Spawner(avango.script.Script):
	''' Manages creation of enemy objects and power ups collectable.
		Also observes position of enemy. If enemy exceeds max bounds,
		it will be removed by the spawner. '''

	def __init__(self):
		self.super(Spawner).__init__()

		# uniform scale factor for spawned objects
		self.spawn_scale = 1.0

		# list of all objects spawned by this instance
		self.spawns_dict = {}

		# parent node for all spawned objects
		self.spawn_root = None

		# vanishing position for spawned objects
		# objects exceeding this plane will be deleted by spawner
		self.z_vanish = 0

		# flag for enabling/disableing automatic spawning
		self.auto_spawn = False

		# number of maximum spawns
		# only used if auto spawn enabled
		self.max_auto_spawns = 10

		# bounds set for random spawning
		# only used if auto spawn enabled
		self.auto_spawn_min_pos = avango.gua.Vec3()
		self.auto_spawn_max_pos = avango.gua.Vec3()

		# enable frame based update
		self.always_evaluate(True)

	def my_constructor(self, PARENT_NODE = None, Z_VANISH = 0, AUTO_SPAWN = True):
		# create root node for object spawning
		self.spawn_root = avango.gua.nodes.TransformNode(Name = "spawn_root")
		self.spawn_root.Transform.value = avango.gua.make_scale_mat(
			self.spawn_scale,
			self.spawn_scale,
			self.spawn_scale
		)
		PARENT_NODE.Children.value.append(self.spawn_root)

		# set members from parameters
		self.z_vanish = Z_VANISH
		self.auto_spawn = AUTO_SPAWN

	def evaluate(self):
		''' frame based update function. '''
		if len(self.spawns_dict) > 0:
			self._remove_vanished()
		if self.auto_spawn:
			self._auto_spawn()

	def _remove_vanished(self):
		''' Removes objects moved out of application bounds. '''
		kill_list = []
		for spawn_id in self.spawns_dict:
			spawn = self.spawns_dict[spawn_id]
			z = spawn.geometry.WorldTransform.value.get_translate().z
			if z > self.z_vanish:
				kill_list.append(spawn_id)
		if len(kill_list) > 0: 
			self.remove_spawns(kill_list)
			while len(kill_list) > 0:
				s = kill_list[0]
				kill_list.pop(0)
			
	def _auto_spawn(self):
		''' Spawns one random object inside configured spawn bounds,
			if number of total spawned objects < self.max_auto_spawns. '''
		if self.spawn_count() < self.max_auto_spawns:
			self.spawn_random(self.auto_spawn_min_pos, self.auto_spawn_max_pos)  

	def spawn_random(self, SPAWN_MIN = avango.gua.Vec3(), SPAWN_MAX = avango.gua.Vec3()):
		''' Spawns random enemy at random location. '''
		x = random.uniform(SPAWN_MIN.x, SPAWN_MAX.x)
		y = random.uniform(SPAWN_MIN.y, SPAWN_MAX.y)
		z = random.uniform(SPAWN_MIN.z, SPAWN_MAX.z)

		m = avango.gua.make_trans_mat(x, y, z)

		enemy = None
		enemy_type = random.randint(0,2)
		if enemy_type == 0:
			enemy = Monkey()
		elif enemy_type == 1:
			enemy = Sphere()
		elif enemy_type == 2:
			enemy = Box()

		enemy.my_constructor(PARENT_NODE = self.spawn_root, SPAWN_TRANSFORM = m)
		enemy.movement_speed = random.uniform(0.05, 0.15)
		enemy.rotation_speed = random.uniform(0.5,5.0)
		enemy.rotation_axis.x = random.uniform(0.0,1.0)
		enemy.rotation_axis.y = random.uniform(0.0,1.0)
		enemy.rotation_axis.z = random.uniform(0.0,1.0)
		enemy.rotation_axis.normalize()
		enemy.setScale(random.uniform(self.spawn_scale*0.5,self.spawn_scale*1.5))

		self.spawns_dict[enemy.game_object_id] = enemy

	def clear(self):
		''' Removes all spawned objects, spawned by this instance. '''
		self.remove_spawns(spawns_dict.keys())

	def remove_spawn(self, SPAWN_ID):
		''' Removes an object spawned by this instance. 
			Returns success of removal. TODO fix memory leak'''
		if SPAWN_ID in self.spawns_dict:
			spawn = self.spawns_dict[SPAWN_ID]
			spawn.geometry.Parent.value.Children.value.remove(spawn.geometry)
			self.spawns_dict.pop(SPAWN_ID, spawn)
			del spawn
			return True
		print("FAILURE: Spawn not found (id:", SPAWN.id, ")")
		return False

	def remove_spawns(self, SPAWNS_IDS):
		''' Removes all objects listed in SPAWNS from the list of spawned objects. 
			Returns True if all list elements where removed successfully. '''
		if len(SPAWNS_IDS) == 0:
			return True
		success = True
		for spawn_id in SPAWNS_IDS:
			if not self.remove_spawn(spawn_id):
				success = False
		return success

	def spawn_count(self):
		''' returns total number of objects spawned by this instance. '''
		return len(self.spawns_dict)