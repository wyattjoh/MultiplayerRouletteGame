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
import time
import graphics
import threading



class Game(threading.Thread):
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
        super().__init__()

        self.new_player_lock = threading.Lock()
        self.game_lock_event = threading.Event()
        self.new_player_event = threading.Event()

        self.new_move_lock = threading.Lock()
        self.new_move_event = threading.Event()

        self.start()
        
        
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
        
        # Arduino mailbox
        self._arduino_mailbox = []
        self._arduino_mailbox_lock = threading.Lock()

        # GUI instance
        self._display = graphics.GUI()

        
    def add_new_player(self):
        """
        Creates a player if there is room, and adds to player list.
        
        Returns player_id in the range of (0,8) [Inclusive] if successful.
        
        Failure (full game) returns a -1.
        """
        avatar = -1
        with self.new_player_lock:
            # Returns player_id/avatar code if successful, else -1
            if ((len(self._player_list) < self._player_limit) and 
                self._game_phase == 0):
                avatar = self._avatars.pop(0)
                self._player_list.append(player.Player(avatar, avatar))
                self.new_player_event.set()
                # GUI UPDATE, ADD PLAYER TO DISPLAYED LIST
        
        return avatar

        
    def lock_game(self):
        """
        Starts the game, locking in all players.
        """
        self.game_lock_event.set()
        # GUI UPDATE, DRAW THE WHEEL
        

    def new_pot(self):
        """
        Randomly generates a new pot value for the round.
        Boundaries set between min_pot and max_pot
        """
        # Boundaries for pot size
        min_pot = 1
        max_pot = 10
        self._pot = random.randint(min_pot, max_pot)
    
    
    def add_new_move(self, player, move):
        """
        Adds a move into the move queue from player.
        Player's moved flag is set to True, to prevent multiple additions
        """
        with self.new_move_lock:
            if self._player_list[player].has_moved() == False:
                self._move_queue.append(move)
                self._player_list[player].made_move()
                self.new_move_event.set()

        
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

        if self._pot <= 0:
            text = "lost"
        else:
            text = "won"

        print("Avatar: %d %s %d points!" % (winner.get_avatar(), text, self._pot))
        
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

        with self._arduino_mailbox_lock:
            self._arduino_mailbox = [ x for x in range(len(self._player_list)) ]

        # UPDATE GUI FOR MOVE STATUS, POT, ROUND COUNT
        # TODO: Update arduino state strings
        
        
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
        # TODO: Update arduino state strings


    def init_arduino(self, avatar_id):
        return self.get_state_string(avatar_id, True)

    def get_state_string(self, avatar_id, ovr=False):
        with self._arduino_mailbox_lock:
            if avatar_id in self._arduino_mailbox:
                ovr = True
                self._arduino_mailbox.pop(self._arduino_mailbox.index(avatar_id))

        if self._game_phase == 1 and ovr is False:
            return False
        if self._game_phase == 3:
            state = 1
            status = 2
        else:
            state = 0
            status = 0
        avatar = avatar_id
        score = self._player_list[avatar_id].get_score()
        count = len(self._player_list)
        return "%d,%d,%d,%d,%d" % (state, status, avatar, score, count)
    
    
    def run(self):
        self.new_game()

        while True:
            if self._game_phase == 0:
                """
                Allows for players to join
                """

                if self.game_lock_event.is_set():
                    self._game_phase = 1
                if self.new_player_event.is_set():
                    with self.new_player_lock:
                        # DO GUI UPDATE FOR THE NEW PLAYER THAT IS ADDED
                        self.new_player_event.clear()
                """
                Goes through game phases 1,2,3
                1: Waiting for all moves to be submitted
                2: Executes all moves
                3: Game over, winner declared
                """
            elif self._game_phase == 1:
                if self.new_move_event.wait():
                    with self.new_move_lock:
                        # GUI UPDATE FOR MOVE INDICATOR FOR THAT PLAYER

                        if len(self._move_queue) == len(self._player_list):
                            self._game_phase = 2

                        self.new_move_event.clear()
            elif self._game_phase == 2:
                self.execute_moves()
            elif self._game_phase == 3:
                # DISPLAY THE WINNER
                self.game_over()
