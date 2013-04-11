"""
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
    
    DUE TO THE NETWORKED NATURE OF OUR PROJECT, DOCTESTS ARE IMPRACTICAL.
    
    This is the main game file, which handles the game state, and deals with
    input/output. It directly manipulates the GUI for display as well.
    
"""

import player
import random
import graphics
import threading

# Magic related to adding the shared modules
import sys
sys.path.insert(0, "../")

import shared.core as core

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

        # GUI instance
        self._display = graphics.GUI()

        # Events for thread behaviour
        self.new_player_lock = threading.Lock()
        self.game_lock_event = threading.Event()
        self.new_player_event = threading.Event()
        self.new_move_lock = threading.Lock()
        self.new_move_event = threading.Event()

        # Run thread
        self.start()
    
    
    
    def start_gui(self):
        """
        Used to get tkinter to run in the main thread.
        
        REQUIRED FOR GUI, since tkinter is stupid when using threads.
        """
        self._display.run()
        
        
        
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


        
    def add_new_player(self):
        """
        Creates a player if there is room, and adds to player list.
        
        Returns player_id in the range of (0,8) [Inclusive] if successful.
        
        Failure (full game) returns a -1.
        """
        avatar = -1
        with self.new_player_lock:
            # Checks if there is space for a new player
            if ((len(self._player_list) < self._player_limit) and self._game_phase == 0):
                # Assigns next available id
                avatar = self._avatars.pop(0)
                # Adds to list of players
                self._player_list.append(player.Player(avatar, avatar))
                self._display._player_list = self._player_list
                # Triggers new player events
                self.new_player_event.set()
                self._display.new_player_event.set()
        return avatar


        
    def lock_game(self):
        """
        Starts the game, locking in all players.
        """
        # Does a final update to ensure GUI gets correct variables to display
        self._display._player_list = self._player_list
        self._display._move_queue = self._move_queue
        self._display._pointer = self._pointer
        self._display._pot = self._pot
        self._display._cur_round = self._cur_round
        # Triggers game lock events
        self._display.game_lock_event.set()
        self.game_lock_event.set()
        
        

    def new_pot(self):
        """
        Randomly generates a new pot value for the round.
        Boundaries set between min_pot and max_pot
        """
        # Boundaries for pot size
        min_pot = 1
        max_pot = 10
        self._pot = random.randint(min_pot, max_pot)
        # Updates GUI pot
        self._display._pot = self._pot
    

    
    def add_new_move(self, player, move):
        """
        Adds a move into the move queue from player.
        Player's moved flag is set to True, to prevent multiple additions
        """
        with self.new_move_lock:
            # Prevents multiple moves being submitted by one player
            if self._player_list[player].has_moved() == False:
                # Adds to queue and flags player as having submitted a move
                self._move_queue.append(move)
                self._player_list[player].made_move()
                # Triggers new move events
                self.new_move_event.set()
                self._display.new_move_event.set()

        
        
    def execute_moves(self):
        """
        Executes all moves in the move queue, and awards the pot to the player
        pointed to as the result of all moves.
        """
        # Executes each move, then clears the queue
        self._display._move_queue = self._move_queue
        for move in self._move_queue:
            self._pointer += move
            self._pointer = self._pointer % len(self._player_list)
        self._move_queue = []
        
        # Awards the pot to the winner
        winner = self._player_list[self._pointer]
        score = winner.get_score() + self._pot
        winner.set_score(score)

        # Debug statements
        if self._pot <= 0:
            text = "lost"
        else:
            text = "won"

        core.CoreLogger.debug("Avatar: %d %s %d points!" % (winner.get_avatar(), text, self._pot))
        
        # Advances to next round
        self._cur_round += 1
        self._display._cur_round = self._cur_round
        
        # Checks if game has ended
        if self._cur_round > self._round_limit:
            self._game_phase = 3
        else:
            self._game_phase = 1
            self.new_pot()
        
        # Triggers animation of move execution, wait for completion
        self._display.execution_event.set()
        while self._display.execution_event.is_set():
            pass
        
        # Clears all moved flags for players
        for player in self._player_list:
            player.next_move()
    
        # Updates move status on GUI using an event
        self._display.new_move_event.set()

        with self._arduino_mailbox_lock:
            self._arduino_mailbox = [ x for x in range(len(self._player_list)) ]

        # UPDATE GUI FOR MOVE STATUS, POT, ROUND COUNT
        # TODO: Update arduino state strings
        
        
        
    def game_over(self):
        """
        Declares winner, or winners with highest score, displays on GUI
        """
        # Triggers event to display the winner
        self._display.winner_event.set()



    def init_arduino(self, avatar_id):
        return self.get_state_string(avatar_id, True)



    def get_state_string(self, avatar_id, ovr=False):
        """
        Obtains a string containing information for a particular player. String
        is specially formatted to be sent to the Arduino to update it.
        """
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
        """
        Thread routine. Controls game flow through an infinite while loop.
        """
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
                        self.new_player_event.clear()
                """
                Goes through game phases 1,2,3
                1: Waiting for all moves to be submitted
                2: Executes all moves
                3: Game over, winner declared
                """
            elif self._game_phase == 1:
                # Collect moves from all players
                if self.new_move_event.wait():
                    with self.new_move_lock:
                        # Check if all moves collected
                        if len(self._move_queue) == len(self._player_list):
                            self._game_phase = 2
                        self.new_move_event.clear()
            elif self._game_phase == 2:
                # Execute all collected moves
                self.execute_moves()
            elif self._game_phase == 3:
                self.game_over()