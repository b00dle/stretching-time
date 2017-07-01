#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import random

from lib.game.spawn.Monkey import Monkey
from lib.game.spawn.Sphere import Sphere
from lib.game.spawn.Box import Box
from lib.game.spawn.Cupcake import Cupcake

class Spawner(avango.script.Script):
	''' Manages creation of spawn objects and power ups collectable.
		Also observes position of spawn. If spawn exceeds max bounds,
		it will be removed by the spawner. '''

	def __init__(self):
		self.super(Spawner).__init__()

		# uniform scale factor for spawned objects
		self.spawn_scale = 1.0

		# list of all objects spawned by this instance
		self.spawns_dict = {}

		# parent node for all spawned objects
		self.spawn_root = None

		# flag for enabling/disableing automatic spawning
		self.auto_spawn = False

		# flag for enabling/disabling spawning of pickable objects
		self.spawn_pickable = False

		# number of maximum spawns
		# only used if auto spawn enabled
		self.max_auto_spawns = 10

		# bounds set for random spawning
		# only used if auto spawn enabled
		self.auto_spawn_min_pos = avango.gua.Vec3()
		self.auto_spawn_max_pos = avango.gua.Vec3()

		# lists how many objects have been removed by this spawner
		# useful for counting cup cakes avoided in game
		self.removed_spawns = 0

		# enable frame based update
		self.always_evaluate(True)

	def my_constructor(self, PARENT_NODE = None, AUTO_SPAWN = True):
		# create root node for object spawning
		self.spawn_root = avango.gua.nodes.TransformNode(Name = "spawn_root")
		self.spawn_root.Transform.value = avango.gua.make_scale_mat(
			self.spawn_scale,
			self.spawn_scale,
			self.spawn_scale
		)
		PARENT_NODE.Children.value.append(self.spawn_root)

		# set members from parameters
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
		''' Removes objects moved out of application bounds. '''
		pass
			
	def _auto_spawn(self):
		''' Spawns one random object inside configured spawn bounds,
			if number of total spawned objects < self.max_auto_spawns. '''
		pass

	def spawn(self, SPAWN_MIN = avango.gua.Vec3(), SPAWN_MAX = avango.gua.Vec3(), SPAWN_TYPE = 3):
		pass

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
			self.removed_spawns += 1
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