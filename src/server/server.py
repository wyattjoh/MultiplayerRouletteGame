"""
Usage:    server.py
"""

import time
import docopt
import threading
import socketserver

# Magic related to adding the shared modules
import sys
import os.path
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.comm import extract_data, prepare_data, PORT
from shared.game import SimpleGame, HubController

game_lock = threading.Lock()

game = SimpleGame()
hubs = HubController(game)



class GameCommuncationHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = str(self.request.recv(1024).strip(), "utf-8")
            
        try:
            data = extract_data(self.data)
            print(data)
        except:
            return

        response = {}

        with game_lock:
            if data['type'] is 0:
                # New Hub
                print("<------- New Hub Request ------->")
                hub = hubs.new_hub(data['hub'])
                hub_serial = hub.serialize()
                print(">------- New Hub Request -------<")
            elif data['type'] is 10:
                # State refresh
                print("<------- Refresh Request ------->")
                hub = hubs.get_hub(data['hub'])
                hub.is_alive()
                hub_serial = hub.serialize()
                print(">------- Refresh Request -------<")
            else:
                return

            response['hub'] = hub_serial
            response['gid'] = game.get_gid()

        send_data = prepare_data(response)
        self.request.sendall(send_data)


def play_game(**args):
    while True:
        with game_lock:
            print("\n<-------------->\nGame State")
            game.print_game_state()
            print("\nPlay")
            game.play()
            print("<-------------->")
        time.sleep(10)

if __name__ == "__main__":
    arguments = docopt.docopt(__doc__)

    HOST = "localhost"

    # Create the server, binding to localhost on port outlined in the shared.comm module
    server = socketserver.TCPServer((HOST, PORT), GameCommuncationHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)

    game_thread = threading.Thread(target=play_game, kwargs={'game': game})
    game_thread.daemon = True
    game_thread.start()
    print("Game loop running in thread:", game_thread.name)

    while True:
        time.sleep(60)