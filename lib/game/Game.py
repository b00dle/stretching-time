#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.controller.Spawner import Spawner
from lib.game.controller.DestructionSpawner import DestructionSpawner
from lib.game.player.Player import Player
from lib.game.tool.SwordDyrion import SwordDyrion
from lib.game.tool.PewPewGun import PewPewGun
from lib.game.tool.HomingGun import HomingGun
from lib.game.stage.GameStage import GameStage
from lib.game.stage.PlayStage import PlayStage
import lib.game.Globals

class Game(avango.script.Script):
    ''' Class responsible for managing game logic. '''

    def __init__(self):
        self.super(Game).__init__()

    def my_constructor(self, SCENEGRAPH, HEAD_NODE, SCREEN_NODE, POINTER_INPUT):
        # store scene root
        self.scenegraph = SCENEGRAPH
        self.head_node = HEAD_NODE
        self.screen_node = SCREEN_NODE
        self.pointer_input = POINTER_INPUT
        self.pointer_input.showDebugGeometry(False)

        self._game_over = False

        self.head_pos_buffer = []
        self.velocity_norm = 0.005 # experimentally set 

        # init destruction spawner
        self.destruction_spawner = DestructionSpawner()
        self.destruction_spawner.my_constructor(PARENT_NODE = self.scenegraph.Root.value)

        # init spawner
        self.spawner = Spawner()
        self.spawner.my_constructor(
            PARENT_NODE = self.scenegraph.Root.value,
            Z_VANISH = 2,
            AUTO_SPAWN = False
        )
        
        # init player
        p_offset = avango.gua.make_trans_mat(0,0,0.0) * avango.gua.make_scale_mat(0.1,0.1,0.1)
        self.player = Player()
        self.player.my_constructor(PARENT_NODE = self.screen_node, OFFSET_MAT = p_offset)
        
        # init sword tool
        self.dyrion = SwordDyrion()
        self.dyrion.my_constructor(PARENT_NODE = self.player.node, GEOMETRY_SIZE = 0.5)
        self.dyrion.hide()
        
        # init gun tool
        '''
        self.pewpew = PewPewGun()
        self.pewpew.my_constructor(
            PARENT_NODE = self.player.node,
            SPAWN_PARENT = self.scenegraph.Root.value,
            GEOMETRY_SIZE = 0.3
        )
        self.pewpew.sf_gun_mat.connect_from(self.pointer_input.pointer_node.Transform)
        self.pewpew.sf_gun_trigger.connect_from(self.pointer_input.sf_button)
        '''

        # init homing gun tool
        self.homing = HomingGun()
        self.homing.my_constructor(
            PARENT_NODE = self.player.node,
            SPAWN_PARENT = self.scenegraph.Root.value,
            TARGET_SPAWNER = self.spawner,
            GEOMETRY_SIZE = 0.3
        )
        self.homing.hide()
        
        self.debug_stretch_factor = 2.0

        self.current_stage = PlayStage()
        self.current_stage.my_constructor(GAME=self)
        
        self.always_evaluate(True)

    def evaluate(self):
        ''' Frame base evaluation function to update game logic. '''
        self._move_player()
        if not self._game_over and self.current_stage.is_running():
            self.current_stage.evaluate_stage()

    def _move_player(self):
        ''' Moves player by offset between this and last frame's head position. '''
        head_m = self.head_node.WorldTransform.value
        pos = head_m.get_translate()
        pos.z = 0.0
        self.player.set_transform(pos)

    def start_game(self):
        print("game started.")
        self._game_over = False
        self.current_stage.start()

    def end_game(self, REASON='Player died.'):
        ''' function called when game is over. REASON should specify how the game ended. '''
        print("game over.")
        self.player.bounding_geometry.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(1.0,0.0,0.0,1.0)
        )
        self._game_over = True
        self.current_stage.stop()
        # TODO perform cleanup
        