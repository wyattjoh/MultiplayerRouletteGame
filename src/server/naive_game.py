import player
import random



class Game():
    _player_limit = 9
    _round_limit = 10
    
    def __init__(self):
        self.new_game()
        
        
    def new_game(self):
        """
        Initializes game to play
        """
        self._avatars = [0,1,2,3,4,5,6,7,8]
        self._player_list = []
        
        self._running = 0
        self._game_phase = 0
        
        self._move_queue = []
        self._pointer = 0
        self._pot = 0
        self.new_pot()
        self._cur_round = 1

        
    def add_new_player(self):
        """
        Creates a player, if there is room, and adds to player list
        """
        if (len(self._player_list) < self._player_limit) and self._running == 0:
            avatar = self._avatars.pop(0)
            self._player_list.append(player.Player(avatar, avatar))
            return(avatar)
            # GUI UPDATE, ADD PLAYER TO DISPLAYED LIST
        else:
            return(-1)

        
    def lock_game(self):
        """
        Stops players from joining, begins the game
        """
        self._running = 1
        # GUI UPDATE, DRAW THE WHEEL
        

    def new_pot(self):
        min_pot = -5
        max_pot = 10
        self._pot = random.randint(min_pot, max_pot)
    
    
    def add_new_move(self, player, move):
        if self._player_list[player].has_moved() == False:
            self._move_queue.append(move)
            self._player_list[player].made_move()
            # GUI UPDATE FOR MOVE INDICATOR FOR THAT PLAYER

        
    def execute_moves(self):
        for move in self._move_queue:
            self._pointer += move
            self._pointer = self._pointer % len(self._player_list)
            # UPDATE GUI WITH EACH MOVE
        self._move_queue = []
        
        winner = self._player_list[self._pointer]
        score = winner.get_score() + self._pot
        winner.set_score(score)
        
        for player in self._player_list:
            player.next_move()
        
        self._cur_round += 1
        if self._cur_round > self._round_limit:
            self._game_state = 2
        else:
            self._game_state = 0
            self.new_pot()
        # UPDATE GUI FOR MOVE STATUS, POT, ROUND COUNT
        # UPDATE ARDUINO STATE STRINGS
        
    def game_over(self):
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
        if self._game_state != 2:
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
            if self._running == 0:
                """
                Allows for players to join
                """
                # CHECK FOR NEW PLAYER EVENT
                # CHECK FOR LOCK EVENT
            elif self._running == 1:
                """
                Goes through game states 0,1,2
                0: Waiting for all moves to be submitted
                1: Executes all moves
                2: Game over, winner declared
                """
                if self._game_state == 0:
                    # CHECK FOR NEW MOVE EVENT
                    if len(self._move_queue) == len(self._player_list):
                        self._game_state = 1
                elif self._game_state == 1:
                    self.execute_moves()
                elif self._game_state == 2:
                    # DISPLAY THE WINNER
                    self.game_over()