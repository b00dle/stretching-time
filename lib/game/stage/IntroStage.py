#!/usr/bin/python
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.stage.GameStage import GameStage
import lib.game.Globals

class IntroStage(GameStage):
    ''' Encapsulates main gameplay logic. '''

    sf_next_trigger = avango.SFBool()

    def __init__(self):
        self.super(IntroStage).__init__()

    def my_constructor(self, GAME):
        self.super(IntroStage).my_constructor(GAME)

        self._finalize = False

    def evaluate_stage(self):
        ''' overrides BC functionality. '''
        if self._finalize and not self.sf_next_trigger.value:
            self._game.next_stage()

    def start(self):
        ''' overrides BC functionality. '''
        if self.is_running():
            return
        
        self.super(IntroStage).start()
        
        # add all lifes for player
        while self._game.player.add_life():
            pass
        self._game.player.bounding_geometry.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(0.0,1.0,0.0,1.0)
        )

        self._finalize = False

        # configure hand
        self._game.hand.sf_hand_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_grab_trigger.connect_from(self._game.pointer_input.sf_button)
        # configure trigger for next action in stage
        self.sf_next_trigger.connect_from(self._game.hand.sf_grab_trigger)

        # show all geometries which should be visible in this stage
        self._game.hand.set_active(True)

        # show intro text for game
        self._game.write_text(['Set your player name.',' Press the button to start the game.'], 8)
        
    def stop(self):
        ''' overrides BC functionality. '''
        if not self.is_running():
            return

        self.super(IntroStage).stop()

        # detach trigger for next action in stage
        self.sf_next_trigger.disconnect_from(self._game.hand.sf_grab_trigger)
        # hand
        self._game.hand.sf_hand_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_grab_trigger.disconnect_from(self._game.pointer_input.sf_button)
        # hide all geometries which should be invisible after this stage
        self._game.hand.set_active(False)

        self._game.clear_center_text()

    @field_has_changed(sf_next_trigger)
    def sf_next_trigger_changed(self):
        if self.sf_next_trigger.value and self.is_running():
            self._finalize = True