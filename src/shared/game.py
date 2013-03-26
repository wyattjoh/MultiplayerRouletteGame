import threading
import time
import sys

from random import randint

import os.path
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shared.foundation as foundation

#####################################################
## SHARED BASE COMMUNICATION AND INTERFACE CLASSES ##
#####################################################

class Player(foundation.CoreData):
    """
    Game Player. Used by the Arduino, Hub, and Server.
    """
    # Required by foundation.CoreData
    ident = ['aid']
    fields = ['score']
    private = []

    def __init__(self, player_data):
        self.load(player_data)
        self.score = 0

    def add_score(self, value):
        self.score += int(value)

##################################################
## HUB BASE COMMUNICATION AND INTERFACE CLASSES ##
##################################################

class Hub(foundation.CoreData):
    """
    Game controller Hub
    """
    # Required by foundation.CoreData
    ident = ['hid']
    fields = ['players', 'alive', 'timeout']
    private = ['HOST', 'PORT']

    def __init__(self, hub_data, hid=None):
        self.load(hub_data)

        if hid is not None:
            self.update({'hid': hid})

        print("Hub #{} ini.".format(self.hid))

    def is_alive(self):
        self.update({'alive': True})


b = Hub({'hid': 5})
print("HID: " + str(b.get('hid')))


####################################################
## SERVER BASE COMMUNCATION AND INTERFACE CLASSES ##
####################################################

class HubController:
    def __init__(self, game):
        self.hubs_lock = threading.Lock()
        self.hubs = {}

        self.hid = 0

    def new_hub(self, hub_data):
        """
        Creates a new Hub from JSON or DICT data
        """
        with self.hubs_lock:
            hid = self.hid
            self.hid += 1
        # Loads the hub data, create object
        hub = Hub(hub_data, hid)
        # Add to hubs dict
        with self.hubs_lock:
            self.hubs[hub.get('hid')] = hub
        # Return it's hid
        return hub

    def get_hub(self, hub_data):
        if type(hub_data) is int:
            with self.hubs_lock:
                if hub_data in self.hubs:
                    hub = self.hubs[hub_data]
                    return hub
                else:
                    return None
        else:
            their_hub = Hub(hub_data)
            with self.hubs_lock:
                hub = self.hubs[their_hub.get('hid')]
            return hub

    def get_all_hubs(self):
        return self.hubs

    def _hub_watcher(self, hid):
        with self.hubs_lock:
            hub = self.hubs[hid]

        timeout = hub.get('timeout')

        while time.sleep(2 * timeout):
            if hub.get('alive'):
                hub.update({'alive': False})
            else:
                print("Hub #{} disconnected.".format(hid))
                with self.hubs_lock:
                    del self.hubs[hid]
                sys.exit()

    def hub_watcher(self, hid):
        hub_cleanup_thread = threading.Thread(target=self._hub_watcher, args=(hid,))
        hub_cleanup_thread.daemon = True
        hub_cleanup_thread.start()
        print("Hub Cleanup running in thread:", hub_cleanup_thread.name)

class SimpleGame:
    def __init__(self):

        self.gid = randint(1,500)
        self.clients = {}

        # Ini id's
        self.aid = 1
        self.hid = 1

        print("Game created!")

    def _client_watcher(self, hid):

        pass

    def client_watcher(self, hid):
        hub_cleanup_thread = threading.Thread(target=self._client_cleanup, args=(hid,))
        hub_cleanup_thread.daemon = True
        hub_cleanup_thread.start()
        print("Hub Cleanup running in thread:", hub_cleanup_thread.name)

    def getClient(self, hid):
        if hid in self.clients:
            return self.clients[hid]
        else:
            raise RuntimeError("Invalid hid lookup")

    def newClient(self):
        # Get hid
        hid = self.hid
        
        # Increase hid
        self.hid += 1
        
        # Generate empty dict
        self.clients[hid] = {}

        # Setup the watcher for this client
        self.client_watcher(hid)

        print("New client! ID:{}".format(hid))

        return hid

    def getPlayer(self, player_data):
        if 'hid' in player_data and player_data['hid'] in self.clients:
            client =  self.clients[player_data['hid']]
            if 'aid' in player_data and player_data['aid'] in client:
                player = client[player_data['aid']]
                return player
        raise RuntimeError("Invalid Player lookup")

    def newPlayer(self, player_data):
        if 'hid' in player_data and player_data['hid'] in self.clients:
            client = self.clients[player_data['hid']]
            
            # Get the aid
            aid = self.aid

            # Increase the aid
            self.aid += 1

            # Generate the new player
            client[aid] = Player(aid, player_data)
            
            # Return the aid
            return aid
        raise RuntimeError("Invalid Player lookup")

    def print_game_state(self):
        for hid in self.clients:
            for aid in self.clients[hid]:
                player = self.clients[hid][aid]
                print("Player[{0}] = {1}".format(player.get_aid(), player.getscore()))

    def getAllPlayers(self):
        players = []
        for hid in self.clients:
            for aid in self.clients[hid]:
                players.append(self.clients[hid][aid])
        return players

    def play(self):
        players = self.getAllPlayers()

        if players:
            highest = max(players, key=(lambda x: x.getscore()))

            if highest.getscore() == 0:
                print("No one scored?")
                return

            print("Winner: Player #{0} with {1} points.".format(highest.get_aid(), highest.getscore()))

            self.resetscores(players)

        else:
            print("No players.")

    def resetscores(self, players):
        for player in players:
            player.set_score(0)

    def get_gid(self):
        return self.gid
