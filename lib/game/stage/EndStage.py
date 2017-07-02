#!/usr/bin/python
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.stage.GameStage import GameStage
import lib.game.Globals

class EndStage(GameStage):
    ''' Encapsulates main gameplay logic. '''

    sf_next_trigger = avango.SFBool()

    def __init__(self):
        self.super(EndStage).__init__()

    def my_constructor(self, GAME):
        self.super(EndStage).my_constructor(GAME)

        self._finalize = False

    def evaluate_stage(self):
        ''' overrides BC functionality. '''
        if self._finalize and not self.sf_next_trigger.value:
            self._game.next_stage()
        
    def start(self):
        ''' overrides BC functionality. '''
        if self.is_running():
            return
        
        self.super(EndStage).start()

        self._finalize = False
        
        # configure hand
        self._game.hand.sf_hand_mat.connect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_grab_trigger.connect_from(self._game.pointer_input.sf_button)
        # configure trigger for next action in stage
        self.sf_next_trigger.connect_from(self._game.hand.sf_grab_trigger)

        # show all geometries which should be visible in this stage
        self._game.hand.set_active(True)

        # save player score
        self._game.save_score()

        lines = ['GAME OVER.', '', 'TOP PLAYERS', '', '']
        # show outro text for game
        top_scores = self._game.get_top_scores(15)
        for score in top_scores:
            first = str(score[0])
            while len(first) < 20:
                first += ' '
            second = str(score[1])
            while len(second) < 10:
                second = ' ' + second
            lines.append(first + ' ' + second)
        self._game.write_text(lines, 0)
        
    def stop(self):
        ''' overrides BC functionality. '''
        if not self.is_running():
            return

        self.super(EndStage).stop()

        # detach trigger for next action in stage
        self.sf_next_trigger.disconnect_from(self._game.hand.sf_grab_trigger)
        # hand
        self._game.hand.sf_hand_mat.disconnect_from(self._game.pointer_input.pointer_node.Transform)
        self._game.hand.sf_grab_trigger.disconnect_from(self._game.pointer_input.sf_button)
        # hide all geometries which should be invisible after this stage
        self._game.hand.set_active(False)

        # clear center text
        self._game.clear_center_text()

    @field_has_changed(sf_next_trigger)
    def sf_next_trigger_changed(self):
        if self.sf_next_trigger.value and self.is_running():
            self._finalize = True