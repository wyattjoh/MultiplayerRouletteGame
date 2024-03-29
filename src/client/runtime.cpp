/*
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
    
    Runtime functionality. These functions control all things on the
    Arduino. All calls to serial and graphical functions are handled
    here.
*/

#include <runtime.h>

/*~~~ VARIABLES ~~~*/
// Number of players in game
uint8_t player_count;

// Player score to display
uint8_t player_score;

// Icon to display
uint8_t player_icon;

// Status message to display
uint8_t status_message;

// State of client, determines behaviour, defaulted to 1 (wait for update)
uint8_t client_state = 1;

// Players currently selected move, will be sent
int8_t player_move;

// Offset to send moves with, part of our established protocol
int8_t move_offset;

// Bounds for move selection
int8_t min_move;
int8_t max_move;

// Previous score, used to detect a win
int8_t prev_score;

// Buffer for reading received messages from Python
// Format: S,M,A,PPP,C\n
//  State, Status Message, Avatar, Points (Always 3 digit), Player Count, Null, Newline
char readin[READ_BUFFER];



/*~~~ FUNCTIONS ~~~*/

// Calls initialization for graphics & serial
// Also initializes input for joystick
void client_init(){
  serial_init();
  graphics_init();
  pinMode(BUTTON, INPUT);
  digitalWrite(BUTTON, HIGH);
}



// Initial loading screen, receives first instance of variables
void startup(){
  draw_loading();
  // Wait for initialization message, updates variables when received
  read_update(1);
  // Draws GUI, default starting move is 0
  player_move = 0;
  draw_background();
  update_display();
}



// Processes input to update variables
void read_update(uint8_t init){
  int received = 0;
  // Sends initialization signal if necessary
  while (received != READ_BUFFER-1){
    if(init ==1){
      send_move(-1,0);
    }
    // Reads input from serial
    if(Serial.available() > 0){
      received = serial_readline(readin, READ_BUFFER);
    }
    delay(1000);
  }
  // Updates variables
  update_vars();
}



// Updates client-side variables from readin, converts from ASCII
void update_vars(){
  // Records previous score to check for point gain
  prev_score = player_score;
  // Processes received string to update variables
  client_state = readin[0] - 48;
  status_message = readin[2] - 48;
  player_icon = readin[4] - 48;
  player_score = (readin[6] - 48) * 100;
  player_score += ((readin[7] - 48) * 10);
  player_score += (readin[8] - 48);
  player_count = readin[10] - 48;
  move_offset = ((player_count+1)/2) - 1;
  min_move = -move_offset;
  max_move = player_count/2;
  // Checks for special statuses
  if(player_score > prev_score){
    status_message = 3;
    if(client_state != 0){
      status_message = 4;
    }
  }
}



// Updates scores and other data on screen
void update_display(){
  // Draws player icon, score, move, and status
  draw_player_icon(player_icon);
  draw_score(player_score);
  draw_move(player_move, min_move, max_move);
  draw_status(status_message, player_score-prev_score);
}



// Reads input from joystick to change move selection
void move_select(){
  // If player has an invalid move saved, sets it to 0
  if ((player_move > max_move) || (player_move < min_move)){
    player_move = 0;
  }
  uint8_t selected = 0;
  // Polls analog input to scroll through moves and send when selected
  while(selected == 0){
    // Scroll right
    if((map(analogRead(JOYSTICK),0,1023,0,100)>75) && (player_move < max_move)){
      player_move += 1;
      draw_move(player_move, min_move, max_move);
      delay(500);
    }
    // Scroll left
    if((map(analogRead(JOYSTICK),0,1023,0,100)<25) && (player_move > min_move)){
      player_move -= 1;
      draw_move(player_move, min_move, max_move);
      delay(500);
    }
    // Send selected move
    if(digitalRead(BUTTON)==LOW){
      selected = 1;
      send_move(player_move+move_offset, move_offset);
      client_state = 1;
      status_message = 1;
      draw_status(status_message, 0);
    }
  }
}
