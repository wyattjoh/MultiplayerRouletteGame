#Multiplayer Roulette Game

**Project Members**: Jesse Chu, Wyatt Johnson

**Section**: B2 (Jesse), B1 (Wyatt)

##Introduction
The Multiplayer Roulette Game is a networked multiplayer game featuring a game server/gui utilizing Tkinter, and an Arduino GUI using the Adafruit libraries.

The game is based on a mini-game in Mario Party for Nintendo Wii. The game involves players selecting a value for which will be added to the move queue of the spinner on the board. Whatever player icon the pointer lands on will have that player receive X many more points for successfully winning the odds and getting the points! For example, if there is only two people playing, and both players choose 1, then the pointer will go back around to the initial position.

##Getting Started
1. Starting the **Game Server**:
	* The Game Server files are located in `src/server`
	* Run the: `python3 server.py` command to start
	* It will prompt for an `ip_address`, simply enter the address found by running `ifconfig` or entering it yourself if you know it. You will only need to enter this once, as it remembers the previous value.
	* **NOTE:** Ensure that your networking configuration will allow the hubs to join the server over TCP port `8080`, hub/server communication uses this port.

2. Starting the **Player Hub**:
	* Once the **Game Server** is started, you may continue
	* The Player Hub files are located in `src/hub`
	* Run the: `python3 hub.py` command to start
	* It will prompt for an `ip_address`, simply enter the address of the game server that was obtained in step 1. You will only need to enter this once, as it remembers the previous value.

3. Starting the **Arduino's**:
	* Once the **Game Server** and **Player Hub** have been started, you may continue
	* All Arduino's must have the Arduino Client Firmware loaded onto them, located in `src/client`, run `make upload` to compile and upload the client firmware
	* Once all players have connected their Arduino's running the Arduino Client Firmware to the computer running the Player Hub, follow the onscreen instructions to begin the game