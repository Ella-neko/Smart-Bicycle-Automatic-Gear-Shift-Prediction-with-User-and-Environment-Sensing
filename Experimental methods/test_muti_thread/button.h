const int buttonPin = 8; 
const int LED1 = 6; 
const int LED2 = 7;// the number of the pushbutton pin

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status
int state = 0;
//int buttpress = 0;
void buttonsetup() {
// initialize the pushbutton pin as an input:
  //Serial.begin(9600);
  pinMode(buttonPin, INPUT);

  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  Serial.println("Hello");
//  pinMode(LED3, OUTPUT);
}

void btloop() {
  // read the state of the pushbutton value:    
     digitalWrite(LED1, LOW);
     digitalWrite(LED2, LOW);
     buttonState = digitalRead(buttonPin);

  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
if (buttonState == HIGH) {
    // turn LED on: 
      state++;
      //Serial.println(state);
      delay(500);
}
if(state == 1){
  digitalWrite(LED1, HIGH);
  // digitalWrite(LED2, LOW);
}
if(state == 2){
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, HIGH);
}
if(state == 3){
  digitalWrite(LED1, HIGH);
  digitalWrite(LED2, HIGH);
}
if(state == 4){
  state = 1;
     // Serial.println(state);
}
}


