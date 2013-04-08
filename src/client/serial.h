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
