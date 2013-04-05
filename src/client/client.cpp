// Libraries used
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <SPI.h>

// Main header file
#include <runtime.h>

//DEBUG
uint8_t icon_checker = 0;
uint8_t score_checker = 8;
int8_t move_checker = -4;
uint8_t status_checker = 0;
int8_t min_move = -4;
int8_t max_move = 4;

void setup(){
  // Initializes variables & LCD
  client_init();
  
  // DEBUG
  draw_background();
  draw_player_icon(2);
  draw_score(100);
}

void loop(){
  // DEBUG
  delay(1000);
  draw_player_icon(icon_checker);
  draw_score(score_checker);
  icon_checker++;
  icon_checker = icon_checker%9;
  score_checker = score_checker + 20;
  score_checker = score_checker%200;
  draw_move(move_checker, min_move, max_move);
  if (move_checker >= max_move){
    move_checker = min_move;
  }
  else{
    move_checker = move_checker+1;
  }
  draw_status(status_checker);
  status_checker++;
  status_checker = status_checker%3;
}
