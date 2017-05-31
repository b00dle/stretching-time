#!/usr/bin/python
import avango
import avango.gua
import avango.script

class GameStage(avango.script.Script):
    ''' Class used to encapsulate stages within the game logic.
    Call evaluate_stage to evaluate functionality of stage once. '''

    def __init__(self):
        self.super(GameStage).__init__()

    def my_constructor(self, GAME):
        self._game = GAME
        self._run = False 

    def evaluate_stage(self):
        ''' defines base interface for frame based evaluation functionality. '''
        pass

    def start(self):
        ''' sets up all functionality needed to run this stage. '''
        self._run = True

    def stop(self):
        ''' breaks down all functionality needed to run this stage. '''
        self._run = False

    def is_running(self):
        return self._run

    def cleanup(self):
        ''' cleans up pending connections into the application, so that object can be deleted. '''
        pass