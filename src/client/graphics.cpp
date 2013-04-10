#include <graphics.h>

// Declaration of tft variable
Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);



/*~~~ FUNCTIONS ~~~*/

// Initializes display
void graphics_init(){
  tft.initR(INITR_REDTAB);
  tft.setTextWrap(false);
  tft.setRotation(1);
}



// Displays loading screen
void draw_loading(){
  // Clears screen
  tft.fillScreen(BACKGROUND_COLOR);
  tft.setTextSize(3);
  // Writes text
  tft.setTextColor(TEXT_COLOR);
  tft.setCursor(16, 16);
  tft.println("WAITING");
  tft.setCursor(16, 40);
  tft.println("FOR ALL");
  tft.setCursor(16, 64);
  tft.println("PLAYERS");
  tft.setCursor(16,88);
  tft.println("TO JOIN");
  tft.setTextSize(0);
}



// Draws background for GUI, boxes & labels
void draw_background(){
  // Background fill
  tft.fillScreen(BACKGROUND_COLOR);
  tft.setTextSize(0);
  tft.setTextColor(TEXT_COLOR);
  // Player icon frame
  tft.drawRect(4, 75, 50, 50, FRAME_COLOR);
  tft.drawRect(5, 76, 48, 48, FRAME_COLOR);
  tft.setCursor(8, 79);
  tft.print("Player:");
  // Score frame
  tft.drawRect(58, 75, 98, 50, FRAME_COLOR);
  tft.drawRect(59, 76, 96, 48, FRAME_COLOR);
  tft.setCursor(62, 79);
  tft.print("Score:");
  // Move selection frame
  tft.drawRect(60, 4, 40, 40, FRAME_COLOR);
  tft.drawRect(61, 5, 38, 38, FRAME_COLOR);
  tft.setCursor(64,8);
  tft.print("Move:");
  tft.fillTriangle(55, 8, 55, 40, 47, 24, FRAME_COLOR);
  tft.fillTriangle(104, 8, 104, 40, 112, 24, FRAME_COLOR);
}



// Draws display icon for the player
void draw_player_icon(uint8_t player_icon){
  // Clears previous image (just incase)
  tft.fillRect(6, 88, 46, 35, BACKGROUND_COLOR);
  // Determines color for player
  int16_t color = 0x0000;
  if (player_icon%3 == 0){
    color = RED;
  }
  if (player_icon%3 == 1){
    color = GREEN;
  }
  if (player_icon%3 == 2){
    color = BLUE;
  }
  // Determines shape for player
  if (player_icon == 0 || player_icon == 5 || player_icon == 7){
    tft.fillCircle(28, 104, 12, color);
  }
  if (player_icon == 1 || player_icon == 3 || player_icon == 8){
    tft.fillRect(16, 92, 25, 25, color);
  }
  if (player_icon == 2 || player_icon == 4 || player_icon == 6){
    tft.fillTriangle(16, 117, 41, 117, 28, 92, color);
  }
}



// Displays player's score
void draw_score(uint8_t player_score){
  // Clears previous score
  tft.fillRect(60, 88, 94, 35, BACKGROUND_COLOR);
  tft.setTextColor(TEXT_COLOR);
  tft.setTextSize(3);
  // Displays new score, with leading zeroes
  tft.setCursor(80, 93);
  if (player_score < 100){
    tft.print(0);
  }
  if (player_score < 10){
    tft.print(0);
  }
  tft.print(player_score);
}



// Displays currently selected move
void draw_move(int8_t player_move, int8_t min_move, int8_t max_move){
  // Clears previous move
  tft.fillRect(62, 16, 36, 26, BACKGROUND_COLOR);
  tft.setTextColor(TEXT_COLOR);
  tft.setTextSize(2);
  // Displays new score
  tft.setCursor(68, 20);
  if (player_move >= 0){
    tft.print("+");
  }
  tft.print(player_move);
  // Draws selection arrows as necessary
  if ((player_move > min_move) && (player_move < max_move)){
    tft.fillTriangle(55, 8, 55, 40, 47, 24, FRAME_COLOR);
    tft.fillTriangle(104, 8, 104, 40, 112, 24, FRAME_COLOR);
  }
  if (player_move == min_move){
    tft.fillTriangle(55, 8, 55, 40, 47, 24, UNSELECTED_COLOR);
    tft.fillTriangle(104, 8, 104, 40, 112, 24, FRAME_COLOR);
  }
  if (player_move == max_move){
    tft.fillTriangle(55, 8, 55, 40, 47, 24, FRAME_COLOR);
    tft.fillTriangle(104, 8, 104, 40, 112, 24, UNSELECTED_COLOR);
  }
}



// Displays status messages
void draw_status(int8_t status_message, int8_t winnings){
  // Clears previous message
  tft.fillRect(0, 45, 160, 30, BACKGROUND_COLOR);
  tft.setTextColor(MESSAGE_COLOR);
  tft.setTextSize(1);
  // Displays status message
  if (status_message == 0){
    tft.setCursor(32, 55);
    tft.print("Select your move");
  }
  if (status_message == 1){
    tft.setCursor(54, 48);
    tft.print("Move sent");
    tft.setCursor(6, 60);
    tft.print("Waiting for other players");
  }
  if (status_message == 2){
    tft.setTextSize(2);
    tft.setTextColor(RED);
    tft.setCursor(28, 51);
    tft.print("GAME OVER");
  }
  if (status_message == 3){
    tft.setCursor(54, 48);
    tft.print("Move sent");
    tft.setCursor(6, 60);
    tft.print("You won ");
    tft.print(winnings);
    tft.print(" points!");
  }
}
