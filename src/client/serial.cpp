#include <serial.h>

// Initialize serial port, and clear any lingering bits
void serial_init(){
  Serial.begin(9600);
  Serial.flush();
}
