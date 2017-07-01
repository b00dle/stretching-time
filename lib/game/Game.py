#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.controller.EnemySpawner import EnemySpawner
from lib.game.controller.DestructionSpawner import DestructionSpawner
from lib.game.controller.ToolSpawner import ToolSpawner
from lib.game.controller.PowerUpSpawner import PowerUpSpawner
from lib.game.player.Player import Player
from lib.game.tool.SwordDyrion import SwordDyrion
from lib.game.tool.PewPewGun import PewPewGun
from lib.game.tool.HomingGun import HomingGun
from lib.game.tool.Hand import Hand
from lib.game.stage.IntroStage import IntroStage
from lib.game.stage.PlayStage import PlayStage
from lib.game.stage.EndStage import EndStage
from lib.game.misc.Text import Text
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

        self.game_over = False
        self._game_score = 0

        self.head_pos_buffer = []
        self.velocity_norm = 0.005 # experimentally set 

        # init destruction spawner
        self.destruction_spawner = DestructionSpawner()
        self.destruction_spawner.my_constructor(PARENT_NODE = self.scenegraph.Root.value)

        # init spawner
        self.spawner = EnemySpawner()
        self.spawner.my_constructor(
            PARENT_NODE = self.scenegraph.Root.value,
            AUTO_SPAWN = False,
            Z_VANISH = 2
        )
        
        # init tool spawner
        self.tool_spawner = ToolSpawner()
        self.tool_spawner.my_constructor(
            PARENT_NODE = self.scenegraph.Root.value,
            AUTO_SPAWN = False,
            VANISH_TIME = 3.0
        )

        # power up spawner
        self.powerup_spawner = PowerUpSpawner()
        self.powerup_spawner.my_constructor(
            PARENT_NODE = self.scenegraph.Root.value,
            AUTO_SPAWN = False,
            Z_VANISH = 2
        )

        # init player
        p_offset = avango.gua.make_trans_mat(0,0,0.0) * avango.gua.make_scale_mat(0.1,0.1,0.1)
        self.player = Player()
        self.player.my_constructor(
            PARENT_NODE = self.screen_node,
            OFFSET_MAT = p_offset,
            MAX_LIFE_COUNT=3
        )
        
        # init hand tool
        self.hand = Hand()
        self.hand.my_constructor(
            PARENT_NODE = self.player.node,
            GEOMETRY_SIZE = 2.0,
            TARGET_SPAWNER = self.tool_spawner
        )
        self.hand.set_active(False)

        # init sword tool
        self.dyrion = SwordDyrion()
        self.dyrion.my_constructor(PARENT_NODE = self.player.node, GEOMETRY_SIZE = 0.5)
        self.dyrion.set_active(False)
        
        # init gun tool
        self.pewpew = PewPewGun()
        self.pewpew.my_constructor(
            PARENT_NODE = self.player.node,
            SPAWN_PARENT = self.scenegraph.Root.value,
            GEOMETRY_SIZE = 0.3
        )
        self.pewpew.set_active(False)

        # init homing gun tool
        self.homing = HomingGun()
        self.homing.my_constructor(
            PARENT_NODE = self.player.node,
            SPAWN_PARENT = self.scenegraph.Root.value,
            TARGET_SPAWNER = self.spawner,
            GEOMETRY_SIZE = 0.3
        )
        self.homing.set_active(False)
        
        self.debug_stretch_factor = 2.0

        # list of sequencial stages
        self._stages = [IntroStage(), PlayStage(), EndStage()]
        for stage in self._stages:
            stage.my_constructor(GAME=self)
        self._current_stage = 0

        # init text at center of screen
        self.center_text = Text()
        self.center_text.my_constructor(PARENT_NODE=self.scenegraph.Root.value, TEXT='', SCALE=0.1)
        self.center_text.node.Transform.value = avango.gua.make_trans_mat(0,0,-5)

        # init score text in upper right of screen
        self.score_text = Text()
        self.score_text.my_constructor(PARENT_NODE=self.screen_node, TEXT='0', SCALE=0.05)
        self.score_text.node.Transform.value = avango.gua.make_trans_mat(1.1,0.8,0) 

        self.always_evaluate(True)

    def evaluate(self):
        ''' Frame base evaluation function to update game logic. '''
        self._move_player()
        if self._stages[self._current_stage].is_running():
            self._stages[self._current_stage].evaluate_stage()
        
    def _move_player(self):
        ''' Moves player by offset between this and last frame's head position. '''
        head_m = self.head_node.WorldTransform.value
        pos = head_m.get_translate()
        pos.z = 0.0
        self.player.set_transform(pos)

    def set_game_score(self, SCORE):
        self._game_score = SCORE
        self.score_text.set_text(str(self._game_score))

    def add_game_score(self, VALUE):
        self.set_game_score(self._game_score+int(VALUE))

    def get_game_score(self):
        return self._game_score

    def start_game(self):
        print("game started.")
        self.start_stage(0)

    def start_stage(self, INDEX):
        print("starting stage", str(INDEX % len(self._stages)))
        self._stages[self._current_stage].stop()
        self._current_stage = INDEX % len(self._stages)
        if self._current_stage == 0:
            self.game_over = False
            self.spawner.removed_spawns = 0
            self.set_game_score(0)
        self._stages[self._current_stage].start()

    def next_stage(self):
        self.start_stage(self._current_stage+1)

    def end_game(self, REASON='Player died.'):
        ''' function called when game is over. REASON should specify how the game ended. '''
        print("game over.")
        self.player.bounding_geometry.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(1.0,0.0,0.0,1.0)
        )
        self.game_over = True
        self.start_stage(len(self._stages)-1)
        # TODO perform cleanup
        