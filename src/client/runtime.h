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



/*~~~ FORWARD DECLARATIONS ~~~*/

// Initializes client graphics, serial port, and input
void client_init();

#endif
