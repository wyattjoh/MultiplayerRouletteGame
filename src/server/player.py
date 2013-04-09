"""
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
"""

class Player():
    
    def __init__(self, player_id, avatar, score=0):
        self._player_id = player_id
        self._avatar = avatar
        self._score = int(score)
        self._moved = False
    
    def set_score(self, score):
        if score < 0:
            score = 0
        self._score = int(score)
        
    def made_move(self):
        self._moved = True

    def next_move(self):
        self._moved = False
        
    def get_avatar(self):
        return(self._avatar)
    
    def get_score(self):
        return(self._score)
    
    def has_moved(self):
        return(self._moved)