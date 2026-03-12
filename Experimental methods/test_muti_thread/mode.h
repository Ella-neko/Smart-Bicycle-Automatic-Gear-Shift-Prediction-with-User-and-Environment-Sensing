const int mdPin = 4; 
const int LED3 = 13; 


// variables will change:
int modeState = 0;         // variable for reading the pushbutton status
int mode = 0;

void mdsetup() {
// initialize the pushbutton pin as an input:
 // Serial.begin(9600);
  pinMode(mdPin, INPUT);
  pinMode(LED3, OUTPUT);
 // digitalWrite(LED3, LOW);
}

void mdloop() {
  // read the state of the pushbutton value:
     modeState = digitalRead(mdPin);
  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
     if (modeState == HIGH) {
    // turn LED on: 
      digitalWrite(LED3, HIGH);
      mode++;
      delay(500);
}
}



