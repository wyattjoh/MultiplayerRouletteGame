import threading
import time

import queue
import platform
import serial
import glob

# Magic related to adding the shared modules
import sys
import os
sys.path.insert(0, "../")

import shared.core as core


class ArduinoWatcher(threading.Thread):
    def __init__(self, added_queue, removed_queue):
        super().__init__()
        self.added_queue = added_queue  # Added arduino queue
        self.removed_queue = removed_queue  # Removed arduino queue
        self.arduinos = []  # List of active arduinos

        self._enabled = threading.Event()  # Flag for the arduino watcher's

    def run(self):
        # Wait until the arduino is active, and block here until it is
        while self._enabled.wait():
            system_name = platform.system()  # Get the string
            if system_name == "Windows":
                sys.exit()  # If its windows... quit :)
            elif system_name == "Darwin":
                # Mac uses tty.usbmodem* pattern
                arduinos = glob.glob('/dev/tty.usbmodem*')
            else:
                # Linux uses ttyACM* pattern
                arduinos = glob.glob('/dev/ttyACM*')

            # Add any arduinos in the list that are not in the list already
            for arduino in arduinos:
                if arduino not in self.arduinos:
                    self.added_queue.put(arduino)
                    self.arduinos.append(arduino)

            # Remove any arduinos that are not in the list that were stored
            for arduino in self.arduinos:
                if arduino not in arduinos:
                    self.removed_queue.put(arduino)
                    self.arduinos.remove(arduino)

            # Wait until the added and the removed currently added in
            # this cycle have been processed.

            self.added_queue.join()
            self.removed_queue.join()

    def enable(self):
        # Trigger the enabled event for the scanner
        self._enabled.set()

    def disable(self):
        # Clear the enable event for the scanner
        self._enabled.clear()


class Arduino(threading.Thread):
    max_message_length = 5

    def __init__(self, name):
        super().__init__()

        # Setup initial variables
        self.name = name

        # state variables
        self.state_code = None
        self.state_message = None
        self.avatar_code = None
        self.score = None
        self.player_count = None

        # Set up the threaded variables
        self.output = queue.Queue(1)  # Output from Arduino
        self.input = queue.Queue(1)  # Input to Arduino
        self._died = threading.Event()
        self._registered = threading.Event()

        # State message to respond to the Arduino with
        self.state = None

        # Set up the serial interface
        self.serial = serial.Serial(name, 9600)

    def update_string_from_vars(self):
        # Parse string variables into the string
        self.state = '%d,%d,%d,%03d,%d' % (self.state, self.state_message, self.avatar_code, self.score, self.player_count)

    def disconnected(self):
        # Set the died event
        self._died.set()

    def is_connected(self):
        # Return the ! if the died flag is set
        return not self._died.isSet()

    def update(self, state):
        # Convienence function fot register
        self.register_arduino(state)

    def register_arduino(self, state):
        # Add message to inbox
        message_io = core.StateString._make(state.split(','))
        self.input.put(message_io)
        self._registered.set()

    def _serial_send(self):
        """
        Sends the update state to the Arduino on a regular interval
        """

        try:
            # Check to see if input is a namedtuple object
            if self.state.__class__.__name__ != 'StateString':
                return

            # Load state string
            state_str = self.state

            # Parse statestring as integers
            state = int(state_str.state)
            state_message = int(state_str.state_message)
            avatar_code = int(state_str.avatar_code)
            score = int(state_str.score)
            player_count = int(state_str.player_count)

            # Update instance variables
            self.state_code = state
            self.state_message = state_message
            self.avatar_code = avatar_code
            self.score = score
            self.player_count = player_count

            # Encode message into string, then bytes
            string = "%d,%d,%d,%03d,%d\n" % (state, state_message, avatar_code, score, player_count)
            reencoded = bytes(string, encoding='ascii')

            # Send the bytes over the serial interface
            self.serial.write(reencoded)

        except (serial.serialutil.SerialException, OSError):
            # If there was a SerialException or OSError
            # the client has disconnected
            self.disconnected()

    def _serial_receive(self):
        try:
            # Receive the raw data from serial until
            # it does match an expected input

            recieve_buffer = ""
            message = ""
            while type(message) is str:
                # Read one byte
                raw_message = self.serial.read(1)
                # Convert it to ascii
                recieve_buffer += raw_message.decode('ascii')

                # Check if the last character is a newline
                if ord(recieve_buffer[-1]) != 10:
                    continue
                else:
                    # Remove the newline and carriage return
                    recieve_buffer = recieve_buffer[:-2]

                # Try and turn it into a move string
                try:
                    message = core.MoveString._make(recieve_buffer.split(','))
                except TypeError:
                    # Check if it is longer than the max length, probably a corruption if so
                    if len(recieve_buffer) > Arduino.max_message_length:
                        # So restart it and rebuffer
                        recieve_buffer = ""
                        continue

                # If somehow it turned out to be a string anyways... restart
                if type(message) is str:
                    continue

                # Try and verify if the variables loaded were actually integers
                try:
                    int(message.move)
                    int(message.offset)
                except ValueError:
                    # Else rebuffer and restart
                    message = ""
                    recieve_buffer = ""

            # Return the move object
            return message

        except (serial.serialutil.SerialException, OSError):
            # Else some other socket error occured, so mark the arduino as disconnected
            self.disconnected()

    def run(self):
        while self.is_connected():
            # While it is connected, recieve a message
            serial_input = self._serial_receive()
            # If it is the ini, say we have registered, or wait for it, and then send it the deets
            if int(serial_input.move) is -1 and int(serial_input.offset) is 0:
                # Correct ini recieved, proceed to give them the state
                # 1. Wait until the registration data has been recieved
                self._registered.wait()
                self.state = self.input.get()

                # 2. Send the registration to the arduino
                self._serial_send()

                self.serial.flushInput()

                break

        # While it is still connected, loop
        while self.is_connected():
            # 1. Wait for move from arduino
            # 1.1 Do a blocking read from it until it responds
            #     with soemthing and a newline
            move_string = self._serial_receive()

            # 1.2 Check to see if not ini message
            if int(move_string.move) is -1:
                self.serial.flushInput()
                continue

            # 2. Send move of arduino
            # 2.1 Add move to output queue
            self.output.put(move_string)

            # 3. Wait for new state from server
            # 3.1 Wait until item is gotten from server
            self.state = self.input.get()

            # 3.2 Send via serial to arduino
            self._serial_send()

        core.CoreLogger.debug("%s: Disconnect event recieved." % self.name)


class HubCommunicator(core.CoreComm):
    def __init__(self, ip_address):
        # Init the CoreComm
        super().__init__(ip_address)

        # Set up ini_vars
        self.hub_id = 0
        self._register_hub()

    def _register_hub(self):
        # Get hub_id/register it as a waiting hub
        message = self.send(('register_hub', None))
        self.hub_id = int(message.data)
        core.CoreLogger.debug("Register Hub: %s." % str(self.hub_id))

    def send(self, message):
        # Send if we are only sending the message and type (2 args)
        if len(message) is 2:
            return super().send((self.hub_id, message[0], message[1]))


class PlayerHub(threading.Thread):
    # Config file to load the defaults from
    config_file = "../shared/.env"
    # Config options to save in config_file
    config_options = ['ip_address']

    def __init__(self, user_input, ip_address):
        super().__init__()

        # Setup the user input manager
        self.user_input = user_input

        # Setup the aduino watcher
        self.added_queue = queue.Queue()
        self.removed_queue = queue.Queue()
        self.arduino_watcher = ArduinoWatcher(self.added_queue, self.removed_queue)
        self.arduino_watcher.setDaemon(True)
        self.arduino_watcher.start()

        # Setup the communication handler
        self.comm = HubCommunicator(ip_address)

        # Set up management lists
        self.arduino_count = 0
        self.arduinos = []
        self.move_queue = []

    def update_controllers(self):
        # Get current Arduinos
        arduinos = [arduino for arduino in self.arduinos]

        # Add in detected Arduinos
        while self.added_queue.qsize():
            # Retrive the name from the queue
            arduino_name = self.added_queue.get()

            # Generate a new Arduino object to take care of this
            arduino_obj = Arduino(arduino_name)
            arduino_obj.setDaemon(True)

            core.CoreLogger.debug("Arduino has been detected on port: %s" % arduino_name)

            # Add it to the arduinos list
            arduinos.append(arduino_obj)

            # Mark the task as done
            self.added_queue.task_done()

        arduino_names = [arduino.name for arduino in arduinos]

        # Removed disconnected Arduinos
        while self.removed_queue.qsize():
            arduino = self.removed_queue.get()

            # Reverse lookup the index from the names list
            index = arduino_names.index(arduino)

            core.CoreLogger.debug("Arduino has been removed from port: %s" % arduino)

            # Get a copy of the arduino object and mark it as disconnected
            arduino = arduinos[index]
            arduino.disconnected()

            # Remove references to it in lists
            del arduinos[index]
            del arduino_names[index]

            # Mark this arduino as removed
            self.removed_queue.task_done()

        print("Arduino list:")
        for arduino in arduino_names:
            print("\t%s" % str(arduino))

        # Update the controller references
        self.arduinos = arduinos

    def run(self):
        # Enable the port watcher
        self.arduino_watcher.enable()
        while True:
            os.system('clear')
            print("Press 'l' and [ENTER] to lock current connected Arduinos.\nYou will have 8 seconds for other hubs to join before the game starts...\n")
            if self.user_input.qsize():
                command = self.user_input.get()

                if command == "l":
                    self.arduino_watcher.disable()
                    self.user_input.task_done()
                    break

                self.user_input.task_done()

            # Update the attached controllers and players
            self.update_controllers()

            # Sleep for one, prevents CPU spooling
            time.sleep(1)

        client_number = len(self.arduinos)

        # 1. Register the arduinos
        # 1.1 Send a number of clients connected, it will
        #     return with the ids to assign in a list
        arduino_ids = self.comm.send(('register_arduinos', client_number))
        core.CoreLogger.debug("Got arduino ids: %s" % str(arduino_ids))

        while True:
            # Sleep once, then check
            time.sleep(1)

            # To see if the hub lock has been accepted
            lock_check = self.comm.send(('locked', True))
            if True is lock_check.data:
                break

            # Else print the time left till it is
            if lock_check.data != 0:
                print("%d seconds left..." % lock_check.data)

        # Clear the screen to start the game
        os.system('clear')
        print("Game in progress, see Arduino screens and Game Server Screen.")

        # 2. Init arduinos
        for i in range(client_number):
            game_string = self.comm.send(('init_arduino', arduino_ids.data[i]))
            self.arduinos[i].update(game_string.data)
            self.move_queue.append(False)
            core.CoreLogger.debug("Game State(%s): %s." % (self.arduinos[i].name, str(game_string)))

        # 3. Start arduino threads
        for arduino in self.arduinos:
            arduino.start()

        # 4. Start game
        while True:
            for i in range(client_number):
                arduino = self.arduinos[i]
                if not arduino.output.empty():
                    # Get the message from the arduino
                    message = arduino.output.get()

                    # Get the int of move and offset
                    move = int(message.move)
                    offset = int(message.offset)

                    # Send debug messages to log
                    core.CoreLogger.debug("%s Move from (%d): %d." % (arduino.name, arduino.avatar_code, move - offset))

                    # Send the actual move to the server
                    received = self.comm.send(('arduino_move', (arduino.avatar_code, move - offset)))

                    # If true, then the message was recieved, wait for the updated game status by setting the move_queue[i] to True
                    if received.data is True:
                        self.move_queue[i] = True

                    # Mark the input as processed
                    arduino.output.task_done()

                # If the queue is waiting for a move update, then check for one
                if self.move_queue[i]:
                    game_string_update = self.comm.send(('arduino_state', arduino.avatar_code))
                    if game_string_update.data is not False:
                        arduino.update(game_string_update.data)
                        self.move_queue[i] = False

            # Sleep for half a second to prevent CPU spooling
            time.sleep(0.5)


if __name__ == '__main__':
    # Prepare and/or verify the env file
    config_options = core.load_configuration(PlayerHub.config_file, PlayerHub.config_options)

    # Set up the input queue
    user_input = queue.Queue(1)

    # Set up and launch the playerhub
    ph = PlayerHub(user_input, config_options['ip_address'])
    ph.setDaemon(True)
    ph.start()

    try:
        while True:
            # Infinite while loop running input loop to the input for the user
            val = input()
            user_input.put(val)
    except KeyboardInterrupt:
        pass
