#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import random
import time

from lib.game.spawn.HomingGun import HomingGun
from lib.game.spawn.SwordDyrion import SwordDyrion

class ToolSpawner(avango.script.Script):
	''' Manages creation of spawn objects and power ups collectable.
		Also observes position of spawn. If spawn exceeds max bounds,
		it will be removed by the spawner. '''

	def __init__(self):
		self.super(ToolSpawner).__init__()

		# uniform scale factor for spawned objects
		self.spawn_scale = 1.0

		# list of all objects spawned by this instance
		self.spawns_dict = {}

		# parent node for all spawned objects
		self.spawn_root = None

		# vanishing position for spawned objects
		# objects exceeding this plane will be deleted by spawner
		self.vanish_time = 4.0

		# flag determining whether automatic spawning should be enabled
		self.auto_spawn = True

		# automatically spawns within given interval
		# unit is seconds
		self.spawn_interval = [5.0, 15.0]

		# states what time to reach to perform auto spawn
		# if number is negative no autospawn will be performed
		self.spawn_at = -1.0

		# flag for enabling/disabling spawning of pickable objects
		self.spawn_pickable = False

		# number of maximum spawns
		# only used if auto spawn enabled
		self.max_auto_spawns = 1

		# bounds set for random spawning
		# only used if auto spawn enabled
		self.auto_spawn_min_pos = avango.gua.Vec3()
		self.auto_spawn_max_pos = avango.gua.Vec3()

		# enable frame based update
		self.always_evaluate(True)

	def my_constructor(self, PARENT_NODE = None, VANISH_TIME = 3.0, AUTO_SPAWN = True):
		# create root node for object spawning
		self.spawn_root = avango.gua.nodes.TransformNode(Name = "spawn_root")
		self.spawn_root.Transform.value = avango.gua.make_scale_mat(
			self.spawn_scale,
			self.spawn_scale,
			self.spawn_scale
		)
		PARENT_NODE.Children.value.append(self.spawn_root)

		# set members from parameters
		self.vanish_time = VANISH_TIME
		self.auto_spawn = AUTO_SPAWN

	def evaluate(self):
		''' frame based update function. '''
		if len(self.spawns_dict) > 0:
			self._remove_vanished()
		if self.auto_spawn:
			self._auto_spawn()

	def cleanup(self):
		''' cleans up pending connections into the application, so that object can be deleted. '''
		self.clear()
		if self.spawn_root != None:
			self.spawn_root.Parent.value.Children.value.remove(self.spawn_root)
		self.always_evaluate(False) 

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
				_spawn_type = random.randint(0,1)
				self.spawn(self.auto_spawn_min_pos, self.auto_spawn_max_pos, _spawn_type)

	def spawn(self, SPAWN_MIN = avango.gua.Vec3(), SPAWN_MAX = avango.gua.Vec3(), SPAWN_TYPE = 1):
		''' Spawns random spawn at random location. '''
		self.spawn_at = -1.0

		x = random.uniform(SPAWN_MIN.x, SPAWN_MAX.x)
		y = random.uniform(SPAWN_MIN.y, SPAWN_MAX.y)
		z = random.uniform(SPAWN_MIN.z, SPAWN_MAX.z)

		m = avango.gua.make_trans_mat(x, y, z)

		spawn = None
		if SPAWN_TYPE == 0:
			spawn = HomingGun()
		else:
			spawn = SwordDyrion()

		spawn.pickable = self.spawn_pickable
		spawn.my_constructor(PARENT_NODE = self.spawn_root, SPAWN_TRANSFORM = m)
		spawn.movement_speed = 0.0
		spawn.rotation_speed = random.uniform(0.5,5.0)
		spawn.rotation_axis.x = random.uniform(0.0,1.0)
		spawn.rotation_axis.y = random.uniform(0.0,1.0)
		spawn.rotation_axis.z = random.uniform(0.0,1.0)
		spawn.rotation_axis.normalize()
		spawn.setScale(self.spawn_scale)

		self.spawns_dict[spawn.game_object_id] = spawn

	def clear(self):
		''' Removes all spawned objects, spawned by this instance. '''
		self.remove_spawns(spawns_dict.keys())

	def remove_spawn(self, SPAWN_ID):
		''' Removes an object spawned by this instance. 
			Returns success of removal. TODO fix memory leak'''
		if SPAWN_ID in self.spawns_dict:
			spawn = self.spawns_dict[SPAWN_ID]
			spawn.cleanup()
			self.spawns_dict.pop(SPAWN_ID, spawn)
			del spawn
			return True
		print("FAILURE: Spawn not found (id:", SPAWN_ID, ")")
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