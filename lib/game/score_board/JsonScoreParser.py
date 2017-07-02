#!/usr/bin/python

import json
import os

class JsonScoreParser(object):
    def __init__(self, FILE_NAME):
        self.file_name = FILE_NAME
        self.score_data = None

    def load(self):
        if os.stat(self.file_name).st_size == 0:
            self.score_data = {}
        else:
            with open(self.file_name, 'r') as json_data:
                self.score_data = json.load(json_data)
            
    def write(self):
        with open(self.file_name, 'w') as json_data:
            json.dump(self.score_data, json_data)

    def insert_score(self, PLAYER_NAME, SCORE):
        if self.score_data == None:
            return
        if PLAYER_NAME not in self.score_data:
            self.score_data[PLAYER_NAME] = {}
        self.score_data[PLAYER_NAME]['score'] = SCORE

    def get_top_scores(self, COUNT):
        if self.score_data == None:
            return
        top = [(name, self.score_data[name]['score']) for name in self.score_data]
        top = sorted(top, key=lambda player: player[1], reverse=True)
        if COUNT > len(top):
            return top
        return top[:COUNT]
