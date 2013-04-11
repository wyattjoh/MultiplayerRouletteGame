import time
import threading
import socketserver

# Magic related to adding the shared modules
import sys
sys.path.insert(0, "../")

import shared.core as core
from naive_game import Game

class GameHandler2:
    _lock_timeout = 8

    def __init__(self):
        self.ng = Game()

        # Locks for GameHandler
        self._add_hub_lock = threading.Lock()
        self._locked_hubs_lock = threading.Lock()
        self._timer_lock = threading.Lock()

        self._timer = 0

        self.hub_id = 0
        self._locked_hubs = []

    def new_hub(self):
        hub_id = None
        with self._add_hub_lock:
            hub_id = self.hub_id
            self.hub_id += 1
            with self._timer_lock:
                self._timer = 0
        return hub_id

    def locked_hub(self, hub_id):
        is_locked = False
        with self._locked_hubs_lock:
            if hub_id not in self._locked_hubs:
                self._locked_hubs.append(hub_id)

            with self._add_hub_lock:
                if self.hub_id == len(self._locked_hubs):
                    with self._timer_lock:
                        if self._timer == 0:
                            self._timer = time.time()
                        else:
                            time_left = time.time() - self._timer
                            is_locked = time_left >= self._lock_timeout

                            if is_locked is False:
                                is_locked = self._lock_timeout - int(time_left)

        if is_locked is True:
            self.ng.lock_game()

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
        # self.request is the TCP socket connected to the client
        self.data = self.recieve(self.request)
        core.CoreLogger.debug("Recieved: %s" % str(self.data))

        if self.data.type == 'register_hub':
            response = (self.data.id, self.data.type, gh.new_hub())

        elif self.data.type == 'status':
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
            avatar_id = self.data.data
            game_string = gh.ng.init_arduino(avatar_id)

            response = (self.data.id, self.data.type, game_string)

        elif self.data.type == 'arduino_state':
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

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        core.CoreLogger.debug("Server loop running in thread: {}".format(server_thread.name))

        try:
            gh.ng.start_gui()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    config_options = core.load_configuration(ServerHandler.config_file, ServerHandler.config_options)

    gh = GameHandler2()
    ServerHandler(config_options['ip_address'])
