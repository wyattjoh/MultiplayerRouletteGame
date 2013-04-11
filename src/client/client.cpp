/*
CMPUT 297/115 - Multiplayer Roulette Project - Due 2013-04-11
    Version 1.0 2013-04-09

    By: Jesse H. Chu (1202466)
        Wyatt Johnson (1230799)

    This assignment has been done under the full collaboration model,
    and any extra resources are cited in the code below.
    
    The main client file. Simply calls runtime. Contains the setup/loop
    for the Arduino.
*/

// Libraries used
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <SPI.h>

// Main header file
#include <runtime.h>



void setup(){
  // Initializes variables & LCD
  client_init();
  // Receives initialized variables from python hub
  // Initializes GUI
  startup();
}



void loop(){
  // Move selection mode
  if(client_state == 0){
    move_select();
  }
  // Waiting for python hub response
  else{
    read_update(0);
    update_display();
  }
}
