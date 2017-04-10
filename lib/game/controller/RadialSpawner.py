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

class RadialSpawner(avango.script.Script):
	''' Manages creation of spawned objects. Vanishing by distances to spawn root evaluation. '''

	def __init__(self):
		self.super(RadialSpawner).__init__()

		# uniform scale factor for spawned objects
		self.spawn_scale = 1.0

		# list of all objects spawned by this instance
		self.spawns_dict = {}

		# parent node for all spawned objects
		self.spawn_root = None

		# vanishing distance for spawned objects
		# objects exceeding this plane will be deleted by spawner
		self.vanish_distance = 0

		# enable frame based update
		self.always_evaluate(True)

	def my_constructor(self, PARENT_NODE, VANISH_DISTANCE = 1):
		# create root node for object spawning
		self.spawn_root = avango.gua.nodes.TransformNode(Name = "spawn_root")
		PARENT_NODE.Children.value.append(self.spawn_root)

		# set members from parameters
		self.vanish_distance = VANISH_DISTANCE
	
	def cleanup(self):
		''' cleans up pending connections into the application, so that object can be deleted. '''
		self.clear()
		if self.spawn_root != None:
			self.spawn_root.Parent.value.Children.value.remove(self.spawn_root)
		self.always_evaluate(False)

	def evaluate(self):
		''' frame based update function. '''
		if len(self.spawns_dict) > 0:
			self._remove_vanished()
		
	def _remove_vanished(self):
		''' Removes objects moved out of application bounds. '''
		root_pos = self.spawn_root.WorldTransform.value.get_translate()
		kill_list = []
		for spawn_id in self.spawns_dict:
			spawn = self.spawns_dict[spawn_id]
			spawn_pos = spawn.bounding_geometry.WorldTransform.value.get_translate()
			if (spawn_pos - root_pos).length() > self.vanish_distance:
				kill_list.append(spawn_id)
		if len(kill_list) > 0: 
			self.remove_spawns(kill_list)
			while len(kill_list) > 0:
				s = kill_list[0]
				kill_list.pop(0)
			
	def spawn(self, SPAWN_POS, MOVEMENT_SPEED, MOVEMENT_DIR, SPAWN_TYPE=3, SPAWN_OBJ=None):
		''' Spawns random spawn at random location. '''
		spawn = SPAWN_OBJ
		if spawn == None:
			if SPAWN_TYPE == 0:
				spawn = Monkey()
			elif SPAWN_TYPE == 1:
				spawn = Sphere()
			elif SPAWN_TYPE == 2:
				spawn = Box()
			else:
				spawn = Cupcake()
			spawn.my_constructor(
				PARENT_NODE = self.spawn_root,
				SPAWN_TRANSFORM = avango.gua.make_trans_mat(SPAWN_POS)
			)

		spawn.movement_speed = MOVEMENT_SPEED
		spawn.movement_dir = MOVEMENT_DIR
		spawn.rotation_speed = random.uniform(0.5,5.0)
		spawn.rotation_axis.x = random.uniform(0.0,1.0)
		spawn.rotation_axis.y = random.uniform(0.0,1.0)
		spawn.rotation_axis.z = random.uniform(0.0,1.0)
		spawn.rotation_axis.normalize()
		spawn.setScale(self.spawn_scale)

		self.spawns_dict[spawn.game_object_id] = spawn

	def clear(self):
		''' Removes all spawned objects, spawned by this instance. '''
		self.remove_spawns(self.spawns_dict.keys())

	def remove_spawn(self, SPAWN_ID):
		''' Removes an object spawned by this instance. 
			Returns success of removal. TODO fix memory leak'''
		if SPAWN_ID in self.spawns_dict:
			spawn = self.spawns_dict[SPAWN_ID]
			self.spawns_dict.pop(SPAWN_ID, spawn)
			spawn.cleanup()
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