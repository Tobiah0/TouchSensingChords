#include <Wire.h> //For I2C connection
#include "Adafruit_MPR121.h" // For touch sensor breakout

Adafruit_MPR121 fretSensor = Adafruit_MPR121();
//TODO: Think of button setup for strings

void setup() {
    Serial.begin(115200);
  while (!Serial) { delay(10); } // Wait for serial console
  
  Serial.println("Maker Guitar Initializing...");

  // Initialize the MPR121
  if (!fretSensor.begin(0x5A)) {
    Serial.println("MPR121 not connected");
    while (1);
  }

  //TODO: Initialize string buttons

  void loop() {
    // get current pressed frets
    uint16_t touchedFrets = fretSensor.touched();
    int activeFret = getHighestFret(touchedFrets);

    // Loop through string buttons and playNotes(string_button_press, activeFret)
    for (int s = 0; s < NUM_STRINGS; s++) {
        int currentState = digitalRead(stringPins[s]);
        
        if (currentState == LOW && lastStringState[s] == HIGH) {
        
        // Calculate note: Base string note + fret offset
        int noteToPlay = baseMidiNotes[s] + activeFret;
        
        // Send Note On
        sendMidiNoteOn(noteToPlay, 127); // 127 is max velocity
        currentlyPlayingNotes[s] = noteToPlay; // Remember what note we played
        
        delay(5); // Tiny debounce delay
        } 
        // Check for button release
        else if (currentState == HIGH && lastStringState[s] == LOW) {
        
        // Send Note Off for the specific note that was playing on this string
        if (currentlyPlayingNotes[s] != -1) {
            sendMidiNoteOff(currentlyPlayingNotes[s], 0);
            currentlyPlayingNotes[s] = -1; // Reset playing state
        }
        
        delay(5); // Tiny debounce delay
        }
        
        lastStringState[s] = currentState;
    }
}
//Returns highest fret currently being touched
int getHighestFret(uint16_t touchedData) {
    for (int i = 11; i >= 0; i--) {
      if (touchedData & (1 << i)) {
        return i + 1;
      }
    }
    return 0;
  }

}
