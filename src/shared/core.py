import errno
import json
import socket
import sys
import threading
import queue
import collections

CoreCommStruct = collections.namedtuple('CoreCommStruct', ('id', 'type', 'data'))
StateString = collections.namedtuple('SerialIO', 'state,state_message,avatar_code,score,player_count')
MoveString = collections.namedtuple('MoveString', 'move,offset')

class CoreException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CoreComm:
    HOST = 'localhost' # Default host
    PORT = 8080 # Default port

    def serial(self, data):
        return bytes(json.dumps(data), 'utf-8')

    def unserial(self, data):
        if type(data) is not bytes:
            raise CoreException("Unexpected data type to CoreComm.unserial(data): %s" % type(data))

        return json.loads(str(data, 'utf-8'))

    def send(self, data):
        """
        Send a dictionary to specified HOST:PORT. Returns response dict.
        """
        data = self.serial(data)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create new socket object

            sock.connect((self.HOST, self.PORT)) # Connect to the specified HOST:PORT
            try:
                sock.sendall(data) # Send the bytes to the HOST:PORT
            except socket.error:
                raise CoreException("Send failed!")

            received = self.recieve(sock)

            sock.close()

            return received

        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                raise CoreException("Connection closed by remote host.")
            elif e.errno == errno.ECONNRESET:
                raise CoreException("Server overloaded.")
            else:
                raise

    def recieve(self, socket):

        byte_buffer = ''
        received = ''
        while received.__class__.__name__ != 'CoreCommStruct':
            try:
                byte_buffer += str(socket.recv(2048).strip(), 'utf-8') # Recieve the response from the host
                received = CoreCommStruct._make(json.loads(byte_buffer)) # Try and turn it into a dict
            except ValueError:
                pass

        return received

if __name__ == "__main__":
    pass