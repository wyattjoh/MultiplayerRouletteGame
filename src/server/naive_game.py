"""
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
    
    DUE TO THE NETWORKED NATURE OF OUR PROJECT, DOCTESTS ARE IMPRACTICAL
"""

import player
import random
import graphics



class Game():
    """
    Main game server, runs on a loop
    """
    
    # Hard-coded player and round limits for the game
    _player_limit = 9
    _round_limit = 10
    
    def __init__(self):
        """
        Constructor for the game instance
        """
        self.new_game()
        
        
    def new_game(self):
        """
        Initializes variables for use; Also starts up the GUI
        """
        # Player IDs to be assigned to players
        self._avatars = [0,1,2,3,4,5,6,7,8]
        self._player_list = []
        
        # Gameflow control
        self._game_phase = 0
        
        # Queue of moves to be performed
        self._move_queue = []

        # Current wheel position
        self._pointer = 0
        
        # Points to be won for current round (randomly generated)
        self._pot = 0
        self.new_pot()
        
        # Round counter
        self._cur_round = 1
        
        # GUI instance
        self._display = graphics.GUI()

        
    def add_new_player(self):
        """
        Creates a player if there is room, and adds to player list.
        
        Returns player_id in the range of (0,8) [Inclusive] if successful.
        
        Failure (full game) returns a -1.
        """
        # Returns player_id/avatar code if successful, else -1
        if ((len(self._player_list) < self._player_limit) and 
            self._game_phase == 0):
            avatar = self._avatars.pop(0)
            self._player_list.append(player.Player(avatar, avatar))
            return(avatar)
            # GUI UPDATE, ADD PLAYER TO DISPLAYED LIST
        else:
            return(-1)

        
    def lock_game(self):
        """
        Starts the game, locking in all players.
        """
        self._game_phase = 1
        # GUI UPDATE, DRAW THE WHEEL
        

    def new_pot(self):
        """
        Randomly generates a new pot value for the round.
        Boundaries set between min_pot and max_pot
        """
        # Boundaries for pot size
        min_pot = -5
        max_pot = 10
        self._pot = random.randint(min_pot, max_pot)
    
    
    def add_new_move(self, player, move):
        """
        Adds a move into the move queue from player.
        Player's moved flag is set to True, to prevent multiple additions
        """
        if self._player_list[player].has_moved() == False:
            self._move_queue.append(move)
            self._player_list[player].made_move()
            # GUI UPDATE FOR MOVE INDICATOR FOR THAT PLAYER

        
    def execute_moves(self):
        """
        Executes all moves in the move queue, and awards the pot to the player
        pointed to as the result of all moves.
        """
        # Executes each move, then clears the queue
        for move in self._move_queue:
            self._pointer += move
            self._pointer = self._pointer % len(self._player_list)
            # UPDATE GUI WITH EACH MOVE
        self._move_queue = []
        
        # Awards the pot to the winner
        winner = self._player_list[self._pointer]
        score = winner.get_score() + self._pot
        winner.set_score(score)
        
        # Clears all moved flags for players
        for player in self._player_list:
            player.next_move()
        
        # Advances to next round
        self._cur_round += 1
        if self._cur_round > self._round_limit:
            self._game_phase = 3
        else:
            self._game_phase = 1
            self.new_pot()
        # UPDATE GUI FOR MOVE STATUS, POT, ROUND COUNT
        # UPDATE ARDUINO STATE STRINGS
        
        
    def game_over(self):
        """
        Declares winner, or winners with highest score
        """
        scores = [player.get_score() for player in self._player_list]
        highest = max(scores)
        if scores.count(highest) > 1:
            # GUI DISPLAY MULTIPLE WINNERS
            pass
        else:
            # GUI DISPLAY ONE WINNER
            pass
        # SEND UPDATES TO ARDUINOS


    def get_state_string(self, avatar_id):
        if self._game_phase == 3:
            state = 1
            status = 2
        else:
            state = 0
            status = 0
        avatar = avatar_id
        score = self._player_list[avatar_id].get_score()
        count = len(self._player_list)
        return("%d,%d,%d,%03d,%d" %(state,status,avatar,score,count))
    
    
    def run(self):
        while(True):
            if self._game_phase == 0:
                """
                Allows for players to join
                """
                # CHECK FOR NEW PLAYER EVENT
                # CHECK FOR LOCK EVENT
                """
                Goes through game phases 1,2,3
                1: Waiting for all moves to be submitted
                2: Executes all moves
                3: Game over, winner declared
                """
            elif self._game_phase == 1:
                # CHECK FOR NEW MOVE EVENT
                if len(self._move_queue) == len(self._player_list):
                    self._game_phase = 2
            elif self._game_phase == 2:
                self.execute_moves()
            elif self._game_phase == 3:
                # DISPLAY THE WINNER
                self.game_over()