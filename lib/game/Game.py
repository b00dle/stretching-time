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
from lib.game.controller.SchmeckleSpawner import SchmeckleSpawner
from lib.game.player.Player import Player
from lib.game.tool.SwordDyrion import SwordDyrion
from lib.game.tool.PewPewGun import PewPewGun
from lib.game.tool.HomingGun import HomingGun
from lib.game.tool.Hand import Hand
from lib.game.stage.IntroStage import IntroStage
from lib.game.stage.PlayStage import PlayStage
from lib.game.stage.EndStage import EndStage
from lib.game.misc.Text import Text
from lib.game.spawn.Coin import Coin
from lib.game.score_board.JsonScoreParser import JsonScoreParser
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

        # power up spawner
        self.schmeckle_spawner = SchmeckleSpawner()
        self.schmeckle_spawner.my_constructor(
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

        # score board initialization
        self._score_board = JsonScoreParser('data/scores/scores.json')
        self._score_board.load()

        # list of sequencial stages
        self._stages = [IntroStage(), PlayStage(), EndStage()]
        for stage in self._stages:
            stage.my_constructor(GAME=self)
        self._current_stage = 0

        self.center_text_lines = [Text() for i in range(0,20)]
        y_step = 1.6 / float(len(self.center_text_lines)) 
        for i in range(0, len(self.center_text_lines)):
            self.center_text_lines[i].my_constructor(PARENT_NODE=self.screen_node, TEXT='', SCALE=0.03)
            self.center_text_lines[i].node.Transform.value = avango.gua.make_trans_mat(0,0.8 - i*y_step,0)

        # init score text in upper right of screen
        self.score_text = Text()
        self.score_text.my_constructor(PARENT_NODE=self.screen_node, TEXT='0', SCALE=0.05)
        self.score_text.node.Transform.value = avango.gua.make_trans_mat(1.1,0.8,0)

        # tokenms visualizing if powerups are active
        self.god_coin = Coin()
        self.freeze_coin = Coin()
        self.normaltime_coin = Coin()
        self.twice_coin = Coin()
        init_list = [
            [0, self.god_coin, 'data/textures/powerups/godmode_coin_alpha.png', 'data/textures/powerups/godmode/godmode_coin_white.png'],
            [1, self.freeze_coin, 'data/textures/powerups/freeze_coin_alpha.png', 'data/textures/powerups/freeze/freeze_coin_white.png'],
            [2, self.normaltime_coin, 'data/textures/powerups/normaltime_coin_alpha.png', 'data/textures/powerups/normaltime/normaltime_coin_white.png'],
            [3, self.twice_coin, 'data/textures/powerups/twice_coin_alpha.png','data/textures/powerups/twice/twice_coin_white.png']
        ]
        for l in init_list:
            l[1].my_constructor(
                PARENT_NODE = self.screen_node,
                SPAWN_TRANSFORM = avango.gua.make_trans_mat(0.7 + 0.2*l[0], 0.6, 0) * avango.gua.make_rot_mat(180,0,1,0),
                TEXTURE_PATH = l[2]
            )
            l[1].setScale(0.075)
            l[1].movement_speed = 0.0
            l[1].rotation_speed = 0.0
            l[1].set_secondary_texture(l[3])

        self.always_evaluate(True)

    def write_text(self, LINES, FIRST_LINE=0):
        self.clear_center_text()
        for i in range(len(LINES)):
            if i+FIRST_LINE >= len(self.center_text_lines):
                return
            self.center_text_lines[i+FIRST_LINE].set_text(LINES[i])

    def clear_center_text(self):
        for t in self.center_text_lines:
            t.clear()

    def save_score(self):
        self._score_board.insert_score(self.player.name, self.get_game_score())
        self._score_board.write()

    def get_top_scores(self, COUNT):
        return self._score_board.get_top_scores(COUNT)

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

    def set_player_name(self, NAME):
        self.player.name = NAME

    def get_player_name(self):
        return self.player.name

    def set_game_score(self, SCORE):
        self._game_score = SCORE
        self.score_text.set_text(str(self._game_score))

    def add_game_score(self, VALUE):
        self.set_game_score(self._game_score+int(VALUE))

    def get_game_score(self):
        return self._game_score

    def start_game(self):
        self.start_stage(0)

    def start_stage(self, INDEX):
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
        self.player.bounding_geometry.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(1.0,0.0,0.0,1.0)
        )
        self.game_over = True
        self.start_stage(len(self._stages)-1)
        # TODO perform cleanup
        