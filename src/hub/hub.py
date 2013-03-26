"""
Usage:    client.py <HOST>
"""

import docopt
import socket, errno
import threading
import time
from random import randint

# Magic related to adding the shared modules
import sys
import os.path
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.comm import extract_data, prepare_data, PORT
from shared.game import Hub

class PlayerHub:

    def __init__(self, arguments):

        hub_data = {}
        hub_data['timeout'] = 2
        hub_data['HOST'] = arguments['<HOST>']
        hub_data['PORT'] = PORT

        self.hub_lock = threading.Lock()
        self.hub = Hub(hub_data)

        self.register_hub()

        self.players = []

        while True:
            if self.hub.get('gid') is 0:
                sys.exit()
            time.sleep(1)

    def register_hub(self):
        request = {}
        request['type'] = 0
        request['hub'] = self.hub.dict_serialize()

        received = self.net_send(request)

        with self.hub_lock:
            self.hub.update(received['hub'])

        print("Got: " + str(received['hub']))
        print("Registerd: " + str(self.hub.dict_serialize()))

        print("Hub #{0} Registered in Game #{1}".format(self.hub.get('cid'), self.hub.get('gid')))

        self.hub_connected_dispatch()

    def _hub_connected_dispatch(self):
        print("Dispatch ini")

        timeout = self.hub.timeout
        data = {'type': 10, 'hub': self.hub.dict_serialize()}

        while True:
            try:
                self.net_send(data)
            except socket.error as e:
                if e.errno == errno.ECONNREFUSED:
                    print("State check returned a closed connection.")
                    with self.hub_lock:
                        self.gid = 0
                    sys.exit()
            print("State refreshed: " + str(data))
            time.sleep(timeout)

    def hub_connected_dispatch(self):
        hub_dispatch_thread = threading.Thread(target=self._hub_connected_dispatch)
        hub_dispatch_thread.daemon = True
        hub_dispatch_thread.start()
        print("Player Hub moniter running in thread:", hub_dispatch_thread.name)

    def register_player(self):
        pass

    def net_send(self, data):
        try:
            data = prepare_data(data)
            # Create a socket (SOCK_STREAM means a TCP socket)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.connect((self.hub.HOST, self.hub.PORT))
            try:
                sock.sendall(data)
                # Receive data from the server and shut down
                received = str(sock.recv(2048), "utf-8")
            except socket.error:
                print('Send failed!')
                sys.exit()

            sock.close()

            received = extract_data(received)

            return received
        
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                print("Connection closed by remote host.")
                sys.exit()
            elif e.errno == errno.ECONNRESET:
                print("Server overloaded.")
                sys.exit()
            else:
                raise

def newHub(arguments):
    PlayerHub(arguments)

if __name__ == '__main__':
    # Started directly, parse command line options...
    arguments = docopt.docopt(__doc__)

    newHub(arguments)

    # player_hubs = []

    # i = 9
    # while i is not 0:
    #     i = i - 1
    #     time.sleep(0.25)
    #     player_thread = threading.Thread(target=newHub, args=(arguments,))
    #     player_thread.daemon = False
    #     player_thread.start()
    #     print("Player Hub running in thread:", player_thread.name)
    #     player_hubs.append(player_thread)
