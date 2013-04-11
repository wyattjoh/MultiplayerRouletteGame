/*
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
    
    Header file for serial communication.
    Has Libraries and Forward Declarations.
*/

#ifndef _SERIAL_H
#define _SERIAL_H

// Libraries used
#include <Arduino.h>
#include <SPI.h>



/*~~~ FORWARD DECLARATIONS ~~~*/

// Initializes serial port
void serial_init();

// Sends move across serial as: move,offset
void send_move(int8_t move, int8_t offset);

// Taken from Assignment 3 Client
// Reads serial input into buffer
uint8_t serial_readline(char *line, uint16_t line_size);

#endif
