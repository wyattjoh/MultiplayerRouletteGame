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

// State of client, determines behaviour
int8_t client_state;

// Players currently selected move, will be sent
int8_t player_move;

// Offset to send moves with, part of our established protocol
int8_t move_offset;

// Bounds for move selection
int8_t min_move;
int8_t max_move;



/*~~~ FUNCTIONS ~~~*/

// Calls initialization for graphics & serial
// Also initializes input for joystick
void client_init(){
  serial_init();
  graphics_init();
  pinMode(BUTTON, INPUT);
  digitalWrite(BUTTON, HIGH);
}
