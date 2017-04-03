#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.controller.RadialSpawner import RadialSpawner

import random

class DestructionSpawner(avango.script.Script):

	def __init__(self):
		self.super(DestructionSpawner).__init__()

		self._spawners = []

		self.always_evaluate(True)

	def my_constructor(self, PARENT_NODE):
		self.parent_node = PARENT_NODE

	def evaluate(self):
		if len(self._spawners) > 0:
			self._remove_unused()

	def _remove_unused(self):
		''' removes unused radial spawners. '''
		kill_list = []
		for spawner in self._spawners:
			if len(spawner.spawns_dict) == 0:
				kill_list.append(spawner)

		while len(kill_list) > 0:
			spawner = kill_list[-1]
			kill_list.pop(0)
			self._spawners.remove(spawner)
			self.parent_node.Children.value.remove(spawner.spawn_root)
			del spawner

	def spawn_destruction(self, SPAWN_POS, SPAWN_SCALE, SPAWN_AMOUNT, VANISH_DISTANCE):
		''' spawns a number of objects for destruction simulation. '''
		spawner = RadialSpawner()
		spawner.my_constructor(
			PARENT_NODE = self.parent_node,
			VANISH_DISTANCE = VANISH_DISTANCE
		)
		spawner.spawn_root.Transform.value = avango.gua.make_trans_mat(SPAWN_POS)

		for i in range(0, SPAWN_AMOUNT):
			spawner.spawn_scale = SPAWN_SCALE * random.uniform(0.5,1.5)
			direction = avango.gua.Vec3()
			while direction.length() == 0:
				direction.x = random.uniform(-1.0,1.0)
				direction.y = random.uniform(-1.0,1.0)
				direction.z = random.uniform(-1.0,1.0)
			direction.normalize()
			speed = random.uniform(0.08, 0.18)
			spawner.spawn(avango.gua.Vec3(0,0,0), speed, direction)

		self._spawners.append(spawner)

