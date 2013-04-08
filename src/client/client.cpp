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
