# Multiplayer Roulette Game

**Project Members**: Jesse Chu, Wyatt Johnson

**Section**: B2 (Jesse), B1 (Wyatt)

## Description

We plan to implement a multiplayer game, where each player utilizes their Arduino as a controller/client. The main game will be hosted on a single computer, running the Python game server. The Python Game Server will communicate with anywhere from 1 to 3 Python Arduino Hubs on the client computers where there could be anywhere from 1 to 3 Arduino Clients connected. This allows for up to 9 players to play simultaneously.

The Arduino will consist of a screen/joystick combo, where information relevant to the current game state will be displayed for the given player. Commands will be interpreted on the Arduino hardware, and once a relevant selection has been made, will have the discrete data sent to the Python Arduino Hub for buffering and passing to the Python Game Server.

The game itself consists of players being assigned slots of a roulette wheel. Each round every player sends the number of spots that they wish for the wheel to turn. The game will execute all of these instructions, and the player whose slot ends up being selected after this gains the points for the round. The point value of the round is randomly determined each round, and may be either positive or negative. The game concludes after 10 rounds.