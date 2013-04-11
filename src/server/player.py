"""
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
    
    The Player class. Used to track the data for each player in the game.
    
    Provides setters and getters for all required access.
"""

class Player():
    """
    Player class. Used to track player stats during gameplay.
    """
    
    def __init__(self, player_id, avatar, score=0):
        """
        Constructor for Player class.
        """
        self._player_id = player_id
        self._avatar = avatar
        self._score = int(score)
        self._moved = False
    
    
    
    def set_score(self, score):
        """
        Sets player score, which will go no lower than zero.
        """
        if score < 0:
            score = 0
        self._score = int(score)
        
        
        
    def made_move(self):
        """
        Sets moved flag to True. Used to indicate which players have made their
        move on the GUI.
        """
        self._moved = True



    def next_move(self):
        """
        Resets moved flag to False. Allows for players to submit moves again for
        the next round.
        """
        self._moved = False
        
        
        
    def get_avatar(self):
        """
        Returns the avatar code for the player. Used in Arduino communication.
        """
        return(self._avatar)
    
    
    
    def get_score(self):
        """
        Returns the score for the player. Used in Arduino communication, as well
        as GUI score display.
        """
        return(self._score)
    
    
    
    def has_moved(self):
        """
        Getter for moved flag. Used to check what players have yet to make their
        move.
        """
        return(self._moved)