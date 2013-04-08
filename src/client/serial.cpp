#include <serial.h>

/*~~~ FUNCTIONS ~~~*/

// Initialize serial port, and clear any lingering bits
void serial_init(){
  Serial.begin(9600);
  Serial.flush();
}



// Sends move across serial as move,offset
void send_move(int8_t move, int8_t offset){
  Serial.print(move);
  Serial.print(",");
  Serial.println(offset);
}



// TAKEN FROM ASSIGNMENT 3 CLIENT
// Reads serial input into buffer
uint8_t serial_readline(char *line, uint16_t line_size){
  uint8_t bytes_read = 0;    // Number of bytes read from the serial port.

  // Read until we hit the maximum length, or a newline.
  while (bytes_read < line_size) {
    while (Serial.available() == 0) {
      // There is no data to be read from the serial port.
      // Wait until data is available.
    }

    line[bytes_read] = (char) Serial.read();

    // A newline is given by \r or \n, or some combination of both
    // or the read may have failed and returned 0
    if (line[bytes_read] == '\r' || line[bytes_read] == '\n') {
      // We ran into a newline character!  Overwrite it with \0
      break;    // Break out of this - we are done reading a line.
    }
    else {
      bytes_read++;
    }
  }

  // Add null termination to the end of our string.
  line[bytes_read] = '\0';
  return bytes_read;
}
