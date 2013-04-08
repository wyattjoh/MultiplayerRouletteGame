import threading
import time

import queue
import platform
import serial
import glob

# Magic related to adding the shared modules
import sys
import os
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shared.core as core

class ArduinoWatcher(threading.Thread):
    def __init__(self, added_queue, removed_queue):
        super().__init__()
        self.added_queue = added_queue
        self.removed_queue = removed_queue
        self.arduinos = []

        self._enabled = threading.Event()

    def run(self):
        while self._enabled.wait():
            system_name = platform.system()
            if system_name == "Windows":
                # Scan for available ports.
                available = []
                for i in range(256):
                    try:
                        s = serial.Serial(i)
                        available.append(i)
                        s.close()
                    except serial.SerialException:
                        pass
                arduinos = available
            elif system_name == "Darwin":
                # Mac
                arduinos = glob.glob('/dev/tty.usbmodem*')
            else:
                # Assume Linux or something else
                arduinos = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')

            for arduino in arduinos:
                if arduino not in self.arduinos:
                    self.added_queue.put(arduino)
                    self.arduinos.append(arduino)

            for arduino in self.arduinos:
                if arduino not in arduinos:
                    self.removed_queue.put(arduino)
                    self.arduinos.remove(arduino)

            # Wait until the added and the removed currently added in this cycle have been processed.
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
        self.recieved = None

        # state variables
        self.state = None
        self.state_message = None
        self.avatar_code = None
        self.score = None
        self.player_count = None


        # Set up the threaded variables
        self.output = queue.Queue(1) # Output from Arduino
        self.input = queue.Queue(1) # Input to Arduino
        self._died = threading.Event()
        self._registered = threading.Event()

        # State message to respond to the Arduino with
        self.state = None

        # Set up the serial interface
        self.serial = serial.Serial(name, 9600)

    def update_string_from_vars(self):
        self.state = '%d,%d,%d,%03d,%d' % (self.state, self.state_message, self.avatar_code, self.score, self.player_count)

    def disconnected(self):
        self._died.set()

    def is_connected(self):
        return not self._died.isSet()

    def update(self, state):
        self.register_arduino(state)

    def register_arduino(self, state):
        message_io = core.SerialIO._make(state)
        self.input.put(message_io)
        self._registered.set()

    def _serial_send(self):
        """
        Sends the update state to the Arduino on a regular interval
        """

        try:
            # Check to see if input is a namedtuple object
            if self.state.__class__.__name__ != 'SerialIO':
                return

            # Encode message into string, then bytes
            string = "%d,%d,%d,%03d,%d\n" % self.state
            reencoded = bytes(string, encoding='ascii')

            # Send the bytes over the serial interface
            self.serial.write(reencoded)

        except (serial.serialutil.SerialException, OSError):
            # If there was a SerialException or OSError, the client has disconnected
            self.disconnected()

    def _serial_receive(self):
        try:
            # Receive the raw data from serial until it does match an expected input
            recieve_buffer = ""
            message = ""
            while message == "":
                raw_message = self.serial.read(1)
                recieve_buffer += raw_message.decode('ascii')

                if ord(recieve_buffer[-1]) != 10:
                    continue
                else:
                    recieve_buffer = recieve_buffer[:-2]

                try:
                    message = core.MoveString._make(recieve_buffer.split(','))
                except TypeError:
                    if len(recieve_buffer) > Arduino.max_message_length:
                        recieve_buffer = ""
                        continue
                break

            return message

        except (serial.serialutil.SerialException, OSError):
            self.disconnected()

    def run(self):
        while self.is_connected():
            serial_input = self._serial_receive()
            if int(serial_input.move) is -1 and int(serial_input.offset) is 0:
                # Correct ini recieved, proceed to give them the state
                
                # 1. Wait until the registration data has been recieved
                self._registered.wait()
                # 2. Send the registration to the arduino
                self._serial_send()

        while self.is_connected():
            # 1. Wait for move from arduino
            move_string = self._serial_receive()

            # 2. Send move of arduino
            # 2.1 Add move to output queue
            self.output.put(move_string)

            # 3. Wait for new state from server
            # 3.1 Wait until item is gotten from server
            self.state = self.input.get()

            # 3.2 Send via serial to arduino
            self._serial_send()

        print("%s: Disconnect event recieved." % self.name)


class HubCommunicator(core.CoreComm):
    def __init__(self):
        super().__init__()

        self.hub_id = 0
        self._register_hub()

    def _register_hub(self):
        message = self.send(('register_hub', None))
        self.hub_id = int(message.data)
        print("Register Hub: %s." % str(self.hub_id))

    def send(self, message):
        if len(message) is 2:
            return super().send((self.hub_id, message[0], message[1]))


class PlayerHub(threading.Thread):
    def __init__(self, user_input):
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
        self.comm = HubCommunicator()

        self.arduino_count = 0
        self.arduinos = []

    def update_controllers(self):
        # Get current Arduinos
        arduinos = [arduino for arduino in self.arduinos]
        

        # Add in detected Arduinos
        while self.added_queue.qsize():
            arduino_name = self.added_queue.get() # Retrive the name from the queue

            # Generate a new Arduino object to take care of this
            arduino = Arduino(arduino_name) 
            arduino.setDaemon(True)
            # arduino.start()

            print("Arduino has been detected on port: %s" % arduino_name)
            
            # Add it to the arduinos list
            arduinos.append(arduino)

            # Mark the task as done
            self.added_queue.task_done()

        arduino_names = [arduino.name for arduino in arduinos]

        # Removed disconnected Arduinos
        while self.removed_queue.qsize():
            arduino = self.removed_queue.get()
            
            # Reverse lookup the index from the names list
            index = arduino_names.index(arduino)

            print("Arduino has been removed from port: %s" % arduino)
            
            # Get a copy of the arduino object and mark it as disconnected
            arduino = arduinos[index]
            arduino.disconnected()

            # Remove references to it in lists
            del arduinos[index]
            del arduino_names[index]
            
            # Mark this arduino as removed
            self.removed_queue.task_done()

        print("Arduino list: %s" % str(arduino_names))

        # Update the controller references
        self.arduinos = arduinos

    def read_from_arduinos(self):
        pass

    def register_arduino(self, arduino):
        pass

    def run(self):
        # TODO: Print the welcoming message
        
        # Enable the port watcher
        self.arduino_watcher.enable()
        while True:
            if self.user_input.qsize():
                command = self.user_input.get()

                print("Command is %s." % command)

                if command == "l":
                    self.arduino_watcher.disable()
                    print("Lock has been initialized.. New players will be ignored.")
                    self.user_input.task_done()
                    break

                self.user_input.task_done()

            # Update the attached controllers and players
            self.update_controllers()

            time.sleep(1)

        client_number = len(self.arduinos)

        print("%d arduinos locked." % client_number)

        global_locked = True
        while global_locked:
            lock_check = self.comm.send(('locked', True))
            print(lock_check.data)
            time.sleep(3)

        # 1. Register the arduinos
        # 1.1 Send a number of clients connected, it will return with the ids to assign in a list
        arduino_ids = self.comm.send(('register_arduinos', client_number))
        print(arduino_ids)

        # for arduino_id in arduino_ids:
            # pr
        
        
        for arduino in self.arduinos:
            arduino.start()



if __name__ == '__main__':
    # TODO: Ask for the IP address of the host

    user_input = queue.Queue(1)

    ph = PlayerHub(user_input)
    ph.setDaemon(True)
    ph.start()

    try:

        while True:
            val = input()
            user_input.put(val)

    except KeyboardInterrupt:
        pass
