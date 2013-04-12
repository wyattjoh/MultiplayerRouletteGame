import time
import threading
import socketserver

# Magic related to adding the shared modules
import sys
sys.path.insert(0, "../")

import shared.core as core
from naive_game import Game


class GameHandler2:
    # Timer after which the players have to add new hubs after global lock has been init
    _lock_timeout = 8

    def __init__(self):
        # The game
        self.ng = Game()

        # Locks for GameHandler
        self._add_hub_lock = threading.Lock()
        self._locked_hubs_lock = threading.Lock()
        self._timer_lock = threading.Lock()

        # The timer for the hub lock
        self._timer = 0

        # The ini hub id
        self.hub_id = 0
        # The list of locked hubs
        self._locked_hubs = []

    def new_hub(self):
        """
        Creates a new hub instance and adds it to the instance list, also returns the hub id.
        """

        hub_id = None
        # Wait for and obtain lock on the add_hubs item
        with self._add_hub_lock:
            hub_id = self.hub_id
            self.hub_id += 1
            # Wait for and obtain lock on the timer
            with self._timer_lock:
                # And resest it as a new hub has joined
                self._timer = 0

        # Returns the hub_id
        return hub_id

    def locked_hub(self, hub_id):
        """
        Checks for the hub lock and/or locks a
        given hub_id. Returns the number of seconds
        until lock or True if lock has been achevied.
        """

        is_locked = False
        # Wait for locked_hubs_lock
        with self._locked_hubs_lock:
            # Checks to see if the hub is already locked
            if hub_id not in self._locked_hubs:
                # Else add him
                self._locked_hubs.append(hub_id)

            # Waif for add_hub lock
            with self._add_hub_lock:
                # Check to see if all hubs are indeed locked
                if self.hub_id == len(self._locked_hubs):
                    # Update timer
                    with self._timer_lock:
                        if self._timer == 0:
                            # Set to current time if it was zero
                            self._timer = time.time()
                        else:
                            # Check if the time is greater than lockout_timeout
                            time_left = time.time() - self._timer
                            is_locked = time_left >= self._lock_timeout

                            if is_locked is False:
                                is_locked = self._lock_timeout - int(time_left)

        # Lock game if is_locked
        if is_locked is True:
            self.ng.lock_game()

        # Returns the number of seconds until lock or True if lock has been achevied.
        return is_locked


class ThreadedGameCommuncationHandler(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class GameCommuncationHandler(socketserver.BaseRequestHandler, core.CoreComm):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        """
        It will check the type of request, and parse it accordingly
        """
        # self.request is the TCP socket connected to the client
        self.data = self.recieve(self.request)
        core.CoreLogger.debug("Recieved: %s" % str(self.data))

        if self.data.type == 'register_hub':
            # Responds with new hub_id
            response = (self.data.id, self.data.type, gh.new_hub())

        elif self.data.type == 'status':
            # Depreciated, kept for backwards compat
            response = self.data

        elif self.data.type == 'locked':
            hub_id = self.data.id
            response = (self.data.id, self.data.type, gh.locked_hub(hub_id))

        elif self.data.type == 'register_arduinos':
            # data -> number of arduinos to register for this client
            id_array = []
            for client in range(self.data.data):
                player_id = gh.ng.add_new_player()
                id_array.append(player_id)

            response = (self.data.id, self.data.type, id_array)

        elif self.data.type == 'init_arduino':
            # Gets avatar_id and game_string to add it to request
            avatar_id = self.data.data
            game_string = gh.ng.init_arduino(avatar_id)

            response = (self.data.id, self.data.type, game_string)

        elif self.data.type == 'arduino_state':
            # Returns game_String
            avatar_id = self.data.data
            game_string = gh.ng.get_state_string(avatar_id)

            response = (self.data.id, self.data.type, game_string)

        elif self.data.type == 'arduino_move':
            # Send translated move and player.
            avatar_code = int(self.data.data[0])
            move = int(self.data.data[1])
            gh.ng.add_new_move(avatar_code, move)

            response = (self.data.id, self.data.type, True)

        self.request.sendall(self.serial(response))


class ServerHandler:
    config_file = "../shared/.env"
    config_options = ['ip_address']

    def __init__(self, ip_address):
        HOST, PORT = ip_address, core.CoreComm.PORT

        # Create the server, binding to localhost on port outlined in the shared.comm module
        server = ThreadedGameCommuncationHandler((HOST, PORT), GameCommuncationHandler)

        # Start the communication handler
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        core.CoreLogger.debug("Server loop running in thread: {}".format(server_thread.name))

        try:
            # Start the GUI
            gh.ng.start_gui()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    config_options = core.load_configuration(ServerHandler.config_file, ServerHandler.config_options)

    # Start the game handler
    gh = GameHandler2()

    # Start the Server Handler
    ServerHandler(config_options['ip_address'])
