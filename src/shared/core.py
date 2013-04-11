import errno
import json
import socket
import collections
import os
import sys

CoreCommStruct = collections.namedtuple('CoreCommStruct', ('id', 'type', 'data'))
StateString = collections.namedtuple('StateString', 'state,state_message,avatar_code,score,player_count')
MoveString = collections.namedtuple('MoveString', 'move,offset')

import logging as CoreLogger

CoreLogger.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename='CoreLogger.log',level=CoreLogger.DEBUG)

class CoreException(Exception):
    def __init__(self, value):
        CoreLogger.error(value)
        sys.exit()

class CoreComm:
    HOST = '10.0.1.6' # Default host
    PORT = 9000 # Default port
    def __init__(self, ip_address):
        self.HOST = ip_address

    def serial(self, data):
        # Serilalze data into a json string then to utf-8 encoded bytes
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

            try:
                sock.connect((self.HOST, self.PORT)) # Connect to the specified HOST:PORT
            except socket.error:
                raise CoreException("No route to host.")

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

def load_configuration(config_filename, config_options_list):
    """
    Loads and/or creates a configuration file from the desired items in the list supplied.

    Returns a dictionary, with list entries being keys to their values.
    """

    # 1. Check if .env exists, else create it
    if os.path.isfile(config_filename):
        # Is a file, don't need to create it
        pass
    else:
        cf = open(config_filename, 'w')
        cf.close()

    # 2. Open file to check if there is the config options we need there
    with open(config_filename, 'rb') as config_file:
        config_file.seek(0)
        # Is a file, check if the settings are there:
        config_options = {}
        for line in config_file.readlines():
            # Add this value to the dict
            (key, value) = str(line, 'utf-8').strip('\n').split(",")
            config_options[key] = value

    # Check if all entries are here
    for config_option in config_options_list:
        # Checks if supplied value is ok, allows to change if requested
        if config_option in config_options:
            response = input("Use %s as %s? [y/n]: " % (str(config_options[config_option]), str(config_option)))

            if response == 'y':
                continue
            elif response == 'n':
                del config_options[config_option]

        # Asks for a new value if not entered
        if config_option not in config_options:
            value = input("Enter %s> " % config_option)
            config_options[config_option] = value

    # Backs up config to filename supplied
    with open(config_filename, 'w') as config_file:
        config_file.seek(0)
        for config_option in config_options:
            config_file.write("%s,%s\n" % (config_option, config_options[config_option]))

    return config_options

if __name__ == "__main__":
    pass