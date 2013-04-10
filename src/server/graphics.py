"""
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
    
    SINCE THIS IS A GUI, DOCTESTS ARE NOT PRACTICAL
    
    Due to time constraints, most of this code is unoptimized.
    
    It's messy, but it works. Comments should be alright though.
    
    Coordinates for display elements are hard-coded.
"""

import threading
from tkinter import *
import math
import time
import player



class GUI(threading.Thread):
    """
    GUI Class, made in tkinter. To allow for game to run at the same time, it
    runs in a thread (inherits from Thread class)
    """
    def __init__(self):
        """
        Constructor. Also calls the Thread constructor
        """
        super().__init__()
        
        # Various events used to update GUI
        self.new_player_event = threading.Event()
        self.game_lock_event = threading.Event()
        self.new_move_event = threading.Event()
        self.execution_event = threading.Event()
        self.winner_event = threading.Event()
        
        # Copy of variables in game_state, read from to display GUI
        self._player_list = []
        self._move_queue = []
        self._pointer = 0
        self._pot = 0
        self._cur_round = 1
        
        # Variables used to draw/update GUI elements
        self._player_icons = []
        self._player_scores = []
        self._player_score_display = []
        self._player_moved = []
        self._player_move_status = []
        self._player_spots = []
        
        self.draw_init()
        a._game.after(1,a.event_handling)
        a._game.mainloop()        



    def draw_init(self):
        """
        Initial drawing routine, lays out most of the window to start off.
        
        Elements drawn here are static, and are the same every game.
        """
        # Root Window declared here
        self._game = Tk()
        self._game.title("Roulette")
        self._game.geometry("800x600+200+200")
        
        # Background frame to hold primary game display widgets
        self._backdrop = Frame(self._game, background = "dark blue")
        self._backdrop.pack(fill=BOTH, expand=1)
        
        # Score display area
        self._score_area = Canvas(self._backdrop, background="grey50", width=200, height=600)
        self._score_area.pack(side=LEFT, fill=BOTH, expand=1)
        for i in range(100, 500, 40):
            self._score_area.create_line(10,i,190,i, width=3)
        self._score_area.create_line(10,100,10,460,width=3)
        self._score_area.create_line(50,100,50,460,width=2)
        self._score_area.create_line(120,100,120,460,width=2)
        self._score_area.create_line(190,100,190,460,width=3)
        self._score_area.create_text(100,70,text="SCORES",font=("Calibri","32"))
        
        # Display area for roulette wheel
        self._play_area = Canvas(self._backdrop, background="dark green", height=600, width=600)
        self._play_area.pack(side=RIGHT, fill=BOTH, expand=1)
        
        # Roulette Wheel graphics
        self._play_area.create_oval(100,150,500,550,fill="grey50", width=5)
        self._play_area.create_oval(200,250,400,450,fill="black", width=5)
        self._play_area.create_arc(150,125,450,300,start=30,extent=120,style="arc",width=5)
        self._play_area.create_polygon(415,175,445,180,430,150,fill="black")
        self._play_area.create_polygon(185,175,155,180,170,150,fill="black")
        self._play_area.create_text(155,160,text="+",font=("Calibri","24"))
        self._play_area.create_text(445,160,text="-",font=("Calibri","24"))
        
        # Round information graphics
        self._play_area.create_text(100,40,text="ROUND:",font=("Calibri","32"),fill="white")
        self._play_area.create_text(450,40,text="PRIZE:",font=("Calibri","32"),fill="white")
        self._round_display = self._play_area.create_text(200,40,text=self._cur_round,font=("Calibri","32"),fill="white")
        self._prize_display = self._play_area.create_text(535,40,text=self._pot,font=("Calibri","32"),fill="white")
        self._play_area.create_text(450,40,text="PRIZE:",font=("Calibri","32"),fill="white")
        
        
        
    def draw_new_player(self):
        """
        Draws player icons in the score table.
        
        Since player icons are assigned in a certain order, this draws icons
        depending on the number of players that have joined, in accordance to
        that pre-determined order.
        """
        # Draws player icons for all players that are joined
        # Draws Player 1
        if len(self._player_list) >= 1 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_oval(15,105,45,135,fill="red",width=0))
        # Draws Player 2
        if len(self._player_list) >= 2 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_rectangle(15,145,45,175,fill="green",width=0))
        # Draws Player 3
        if len(self._player_list) >= 3 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_polygon(15,215,45,215,30,185,fill="blue"))
        # Draws Player 4
        if len(self._player_list) >= 4 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_rectangle(15,225,45,255,fill="red",width=0))
        # Draws Player 5
        if len(self._player_list) >= 5 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_polygon(15,295,45,295,30,265,fill="green"))
        # Draws Player 6
        if len(self._player_list) >= 6 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_oval(15,305,45,335,fill="blue",width=0))
        # Draws Player 7
        if len(self._player_list) >= 7 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_polygon(15,375,45,375,30,345,fill="red"))
        # Draws Player 8
        if len(self._player_list) >= 8 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_oval(15,385,45,415,fill="green",width=0))
        # Draws Player 9
        if len(self._player_list) >= 9 > len(self._player_icons):
            self._player_icons.append(self._score_area.create_rectangle(15,425,45,455,fill="blue",width=0))
    
    
    
    def draw_player(self):
        """
        Draws player icons on the roulette wheel.
        
        Since player icons are assigned in a certain order, this draws icons
        depending on the number of players that have joined, in accordance to
        that pre-determined order.        
        """
        # Draws roulette wheel icons once game has started
        # Also generates a dictionary of what angles each player's slice sits at
        divide_angle = -2*math.pi/len(self._player_list)
        draw_angle = 0
        draw_x = 300+150*math.cos(draw_angle)
        draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 1
        if len(self._player_list) >= 1:
            self._play_area.create_oval(draw_x-20,draw_y-20,draw_x+20,draw_y+20,fill="red",width=0)
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 2
        if len(self._player_list) >= 2:
            self._play_area.create_rectangle(draw_x-20,draw_y-20,draw_x+20,draw_y+20,fill="green",width=0)
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 3
        if len(self._player_list) >= 3:
            self._play_area.create_polygon(draw_x-20,draw_y+20,draw_x+20,draw_y+20,draw_x,draw_y-20,fill="blue")
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 4
        if len(self._player_list) >= 4:
            self._play_area.create_rectangle(draw_x-20,draw_y-20,draw_x+20,draw_y+20,fill="red",width=0)
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 5
        if len(self._player_list) >= 5:
            self._play_area.create_polygon(draw_x-20,draw_y+20,draw_x+20,draw_y+20,draw_x,draw_y-20,fill="green")
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 6
        if len(self._player_list) >= 6:
            self._play_area.create_oval(draw_x-20,draw_y-20,draw_x+20,draw_y+20,fill="blue",width=0)
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 7
        if len(self._player_list) >= 7:
            self._play_area.create_polygon(draw_x-20,draw_y+20,draw_x+20,draw_y+20,draw_x,draw_y-20,fill="red")
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 8
        if len(self._player_list) >= 8:
            self._play_area.create_oval(draw_x-20,draw_y-20,draw_x+20,draw_y+20,fill="green",width=0)
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)
        # Draws Player 9
        if len(self._player_list) >= 9:
            self._play_area.create_rectangle(draw_x-20,draw_y-20,draw_x+20,draw_y+20,fill="blue",width=0)
            self._player_spots.append(draw_angle)
            draw_angle += divide_angle
            draw_x = 300+150*math.cos(draw_angle)
            draw_y = 350+150*math.sin(draw_angle)            
    
    
    
    def draw_wheel_lines(self):
        """
        Draws dividing lines for the roulette wheel
        """
        # Draws roulette wheel lines once game has started
        divide_angle = -2*math.pi/len(self._player_list)
        half_angle = divide_angle/2
        draw_angle = half_angle
        for player in self._player_list:
            self._play_area.create_line(300,350,300+200*math.cos(draw_angle),350+200*math.sin(draw_angle),width=5)
            draw_angle += divide_angle
    
    
    
    def draw_arrow(self):
        """
        Initializes the arrow for the wheel. Always starts off pointing at
        player 1.
        """
        # Draws arrow pointing at player 1 to begin with
        self._arrow = self._play_area.create_polygon(280,350,300,370,425,350,300,330,fill="yellow")


    
    def spin_arrow(self, angle):
        """
        Draws the arrow at given angle, used to animate the arrow turning.
        """
        # Updates arrow coordinates
        self._play_area.coords(self._arrow,300+20*math.cos(angle+math.pi),350+20*math.sin(angle+math.pi),300+20*math.cos(angle+math.pi/2),350+20*math.sin(angle+math.pi/2),300+125*math.cos(angle),350+125*math.sin(angle),300+20*math.cos(angle-math.pi/2),350+20*math.sin(angle-math.pi/2))
        
        # Displays change in arrow state
        self.refresh_display()
        
        
        
    def flash_arrow(self):
        """
        Flashes arrow red, to indicate move queue completion.
        """
        for i in range(0,2):
            self._play_area.itemconfig(self._arrow, fill="red")
            self.refresh_display()
            time.sleep(0.25)
            self._play_area.itemconfig(self._arrow, fill="yellow")
            self.refresh_display()
            time.sleep(0.25)
        
        
        
    def flash_score(self):
        """
        Flashes the score of the winner of the current prize
        """
        winner = self._player_score_display[self._pointer]
        for i in range(0,2):
            self._score_area.itemconfig(winner,fill="yellow")
            self.refresh_display()
            time.sleep(0.25)
            self._score_area.itemconfig(winner,fill="black")
            self.refresh_display()
            time.sleep(0.25)

    
    def update_moved(self):
        """
        Updates player move status to be displayed.
        
        The first time this function is called, it will generate the canvas
        text items to display this. All subsequent calls will update the items.
        """
        # Checks which players have made their moves
        self._player_moved = [1 if player.has_moved() else 0 for player in self._player_list]
        
        # Generates text items for the first call
        if len(self._player_move_status) == 0:
            draw_x = 155
            draw_y = 120
            for moved in self._player_moved:
                self._player_move_status.append(self._score_area.create_text(draw_x,draw_y,font=("Calibri","20")))
                draw_y+=40
                
        # Displays status
        for i in range(0,len(self._player_list)):
            if self._player_moved[i] == 0:
                self._score_area.itemconfig(self._player_move_status[i],text="WAIT",fill="red")
            else:
                self._score_area.itemconfig(self._player_move_status[i],text="SENT",fill="green")
        self.refresh_display()
    
    
    
    def update_scores(self):
        """
        Updates player scores to be displayed.
        
        The first time this function is called, it will generate the canvas
        text items to display this. All subsequent calls will update the items.
        """
        # Obtains all players' scores to display
        self._player_scores = [player.get_score() for player in self._player_list]
        
        # Generates text items for first call
        if len(self._player_score_display) == 0:
            draw_x = 85
            draw_y = 120
            for score in self._player_scores:
                self._player_score_display.append(self._score_area.create_text(draw_x,draw_y,font=("Calibri","20")))
                draw_y+=40
        
        # Displays scores
        for i in range(0,len(self._player_list)):
            self._score_area.itemconfig(self._player_score_display[i],text=self._player_scores[i])
        self.refresh_display()
    
    
    
    def execute_moves(self):
        """
        Executes move queue and updates display as needed.
        """
        # Executes moves in move queue
        for move in self._move_queue:
            self.do_move(move)
            time.sleep(0.25)
        self.flash_arrow()
        self.update_scores()
        self.flash_score()
        self.update_moved()
        self.round_update()
    
    
    
    def do_move(self, move):
        """
        Performs a single move, changing the player currently pointed at.
        
        Animates the motion of the moving arrow, by turning it through smaller
        angles in order to reach the destination.
        
        Smoothness of animation set by turn_resolution (larger is smoother)
        """
        # Calculates angle difference, sets turn_resolution
        turn_resolution = 100
        delay_factor = 4
        delay_time = 1/(delay_factor*turn_resolution)
        dest = (self._pointer + move) % len(self._player_list)
        cur_angle = self._player_spots[self._pointer]
        dest_angle = self._player_spots[dest]
        turn_angle = -2*math.pi/len(self._player_list)/turn_resolution
        angle_dist = dest_angle-cur_angle
        
        # Turns arrow in the appropriate direction
        if (0 > angle_dist > -math.pi) or (angle_dist >= math.pi):
            while cur_angle != dest_angle:
                # Smaller steps towards destination
                if abs(cur_angle - dest_angle) > abs(turn_angle):
                    cur_angle += turn_angle
                    self.spin_arrow(cur_angle)
                # Termination, reached destination
                else:
                    cur_angle = dest_angle
                    self.spin_arrow(dest_angle)
                # Allows for smooth animation, instead of instantly ending
                time.sleep(delay_time)
                # Corrects any overflow for accepted angle values
                while (cur_angle <= -2*math.pi):
                    cur_angle += 2*math.pi
        elif(0 < angle_dist < math.pi) or (angle_dist <= -math.pi):
            while cur_angle != dest_angle:
                # Smaller steps towards destination
                if abs(cur_angle - dest_angle) > abs(turn_angle):
                    cur_angle -= turn_angle
                    self.spin_arrow(cur_angle)
                # Termination, reached destination
                else:
                    cur_angle = dest_angle
                    self.spin_arrow(dest_angle)
                # Allows for smooth animation, instead of instantly ending
                time.sleep(delay_time)
                # Corrects overflow for accepted angle values
                while (cur_angle > 0):
                    cur_angle -= 2*math.pi
        # Updates pointer value
        self._pointer = dest

    
    
    def show_winner(self):
        final_scores = [player.get_score() for player in self._player_list]
        winner = final_scores.index(max(final_scores))
    
    
    
    def round_update(self):
        """
        Updates display of current round counter and prize display.
        """
        # Formats prize string before display
        prize_display = str(self._pot)
        if self._pot >= 0:
            prize_display = "+"+prize_display
        # Updates displayed values
        self._play_area.itemconfig(self._prize_display, text=prize_display)
        self._play_area.itemconfig(self._round_display, text=self._cur_round)
        self.refresh_display()
    
    
    
    def refresh_display(self):
        """
        Used to display intermediary changes in tkinter.
        """
        self._play_area.update_idletasks()
        self._score_area.update_idletasks()
    
    
    
    def event_handling(self):
        if self.new_player_event.is_set():
            self.draw_new_player()
            self.new_player_event.clear()
        if self.game_lock_event.is_set():
            self.draw_player()
            self.draw_wheel_lines()
            self.draw_arrow()
            self.round_update()
            self.update_scores()
            self.update_moved()    
            self.game_lock_event.clear()
        if self.new_move_event.is_set():
            self.update_moved()
            self.new_move_event.clear()
        if self.execution_event.is_set():
            self.execute_moves()
            self.execution_event.clear()
        self._game.after(1,self.event_handling)
    
    
    
    #self.winner_event = threading.Event()

        
"""
a = GUI()
for i in range(0,9):
    a._player_list.append(player.Player(i,i))
import random
for player in a._player_list:
    player.set_score(random.randint(-50, 200))
    player.next_move()
a._move_queue = [random.randint(-4,4) for i in range(0,9)]
a._pot = 5
a._cur_round = 6
a.new_player_event.set()
a.game_lock_event.set()
a.new_move_event.set()
a.execution_event.set()
a._game.after(1,a.event_handling)
a._game.mainloop()
"""