#ifndef _GRAPHICS_H
#define _GRAPHICS_H

// Libraries used
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <SPI.h>



// Definition for initializing LCD Display
// standard U of A library settings, assuming Atmel Mega SPI pins
#define TFT_CS   6  // Chip select line for TFT display
#define TFT_DC   7  // Data/command line for TFT
#define TFT_RST  8  // Reset line for TFT (or connect to +5V)



// Defined colors here for quick GUI editting
#define BACKGROUND_COLOR  0x0000
#define FRAME_COLOR       0xFFFF
#define TEXT_COLOR        0xFFFF
#define MESSAGE_COLOR     0xFFFF
#define RED               0xF800
#define GREEN             0x07E0
#define BLUE              0x001F



// External declaration of tft
extern Adafruit_ST7735 tft;



/*~~~ FORWARD DECLARATIONS ~~~*/

// Initializes LCD Screen
void graphics_init();

// Loading screen before game starts
void draw_loading();

// Draws background for GUI
void draw_background();

// Displays player's icon
void draw_player_icon(uint8_t player_icon);

// Displays player's score
void draw_score(uint8_t player_score);

// Displays currently selected move
void draw_move(int8_t player_move, int8_t min_move, int8_t max_move);

// Displays status messages
void draw_status(int8_t status_message);

#endif
