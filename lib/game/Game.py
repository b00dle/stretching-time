#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.controller.Spawner import Spawner
import lib.game.Globals

import random

class Game(avango.script.Script):
	''' Class responsible for managing game logic. '''

	def __init__(self):
		self.super(Game).__init__()

	def my_constructor(self, SCENE_ROOT):
		# store scene root
		self.scene_root = SCENE_ROOT

		# init spawner
		self.spawner = Spawner()
		self.spawner.my_constructor(
			PARENT_NODE=self.scene_root,
			Z_VANISH=0.25,
			AUTO_SPAWN=True
		)
		self.spawner.auto_spawn_min_pos = avango.gua.Vec3(-10, -8, 0)
		self.spawner.auto_spawn_max_pos = avango.gua.Vec3(10, 8, 0)

		self.always_evaluate(True)

		self._debug_stretch_factor = 1.0

	def test(self):
		''' debug function for testing purposes. '''
		pass

	def evaluate(self):
		''' Frame base evaluation function to update game logic. '''
		self._time_stretch()

	def _time_stretch(self):
		''' calculates a global factor for all time based animations. '''
		lib.game.Globals.TIME_FACTOR += self._debug_stretch_factor * 0.01
		if lib.game.Globals.TIME_FACTOR > 2.5:
			self._debug_stretch_factor = -1.0
		elif lib.game.Globals.TIME_FACTOR < 0.5:
			self._debug_stretch_factor = 1.0