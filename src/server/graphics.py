"""
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
    
    SINCE THIS IS A GUI, DOCTESTS ARE NOT PRACTICAL
"""

import threading
from tkinter import *
import math
"""
AVATAR MAPPING:
0	RED	CIRCLE
1	GREEN	SQUARE
2	BLUE	TRIANGLE
3	RED	SQUARE
4	GREEN	TRIANGLE
5	BLUE	CIRCLE
6	RED	TRIANGLE
7	GREEN   CIRCLE
8	BLUE	SQUARE
"""


class GUI(threading.Thread):
    
    def __init__(self):
        super().__init__()
        
        self._player_list = []

        self._game_phase = 0
        
        self._move_queue = []
        self._pointer = 0
        self._pot = 0
        self._cur_round = 1


    def draw_init(self):
        # Root Window declared here
        self._game = Tk()
        self._game.title("Roulette")
        self._game.geometry("800x600+200+200")
        
        # Background frame to hold primary game display widgets
        self._backdrop = Frame(self._game, background = "dark blue")
        self._backdrop.pack(fill=BOTH, expand=1)
        
        # Score display area
        self._score_area = Frame(self._backdrop, background = "grey", width=200)
        self._score_area.pack(side=LEFT, fill=BOTH, expand=1)
        
        # Display area for roulette wheel
        self._play_area = Canvas(self._backdrop, background="dark green", height=600, width=600)
        self._play_area.pack(side=RIGHT, fill=BOTH, expand=1)
        
        self._play_area.create_oval(100,150,500,550,fill="grey50", width=5)
        
    def update_game_display(self):
        pass