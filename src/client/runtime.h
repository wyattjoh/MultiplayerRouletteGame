#ifndef _RUNTIME_H
#define _RUNTIME_H

// Libraries used
#include <Arduino.h>
#include <SPI.h>

// Include header files for serial communication and graphics
#include <serial.h>
#include <graphics.h>



// Defines ports for joystick/button
#define JOYSTICK 0
#define BUTTON 4



// Defines read-buffer length
#define READ_BUFFER 12



/*~~~ EXTERNAL VARIABLES ~~~*/

// State of client, determines behaviour
extern uint8_t client_state;



/*~~~ FORWARD DECLARATIONS ~~~*/

// Initializes client graphics, serial port, and input
void client_init();

// Initial loading screen, receives first instance of variables
void startup();

// Reads in input from serial to update variables
void read_update(uint8_t init);

// Updates client-side variables
void update_vars();

// Updates scores and other data on screen
void update_display();

// Processes joystick input to select moves
void move_select();

#endif
