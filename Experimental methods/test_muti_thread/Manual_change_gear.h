

const int buttonPin = 19;    //升檔
const int buttonPin_2 = 18;  //降檔
const int LED1 = 6; 
const int LED2 = 7;// the number of the pushbutton pin

// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status
int buttonState_2 = 0;         // variable for reading the pushbutton status
int state = 0;
int ChangeT1 = 0;
int ChangeT2 = 0;
int Gear = 1;
int checktime = 2000;
//int buttpress = 0;

int  SD_gear_flag2=1;

void changeup(){
  
    //Serial.println("00");
    //delay(2000);
    
    // read the state of the pushbutton value:    
    //digitalWrite(LED1, LOW);
    
    /* buttonState = digitalRead(buttonPin);
    buttonState_2 = digitalRead(buttonPin_2);*/
    
    //ChangeT1 = millis();
    // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
    //while(ChangeT2 - ChangeT1 < checktime){

    if(SD_gear_flag2==1 && gear_flag==1 && Gear<6){
        //buttonState = digitalRead(buttonPin);
        //buttonState_2 = digitalRead(buttonPin_2);
        digitalWrite(LED1, HIGH);
        //ChangeT2 = millis();
        //digitalWrite(LED2, HIGH);
        //checktime += 200;
        Gear++;
        //delay(1000);
        //digitalWrite(LED2, LOW);
        //Serial.print("Gear1:");
        //Serial.println(Gear);
        gear_flag=0;
    }
    digitalWrite(LED1, LOW);
    //Serial.print("Gear:");
    //Serial.println(Gear);
    //delay(1000);
    //MsTimer2::start();
    //motorloop(2);
    
}

void changedown(){
    //Serial.println("11");
    //delay(2000);
    // read the state of the pushbutton value:    
    
    //digitalWrite(LED1, LOW);
    
    /* buttonState = digitalRead(buttonPin);
    buttonState_2 = digitalRead(buttonPin_2);*/
    
    //ChangeT1 = millis();
    // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
    //while(ChangeT2 - ChangeT1 < checktime){
    if(SD_gear_flag2==1 && gear_flag==1 && Gear>1){
        //buttonState = digitalRead(buttonPin);
        //buttonState_2 = digitalRead(buttonPin_2);
        digitalWrite(LED1, HIGH);
        //ChangeT2 = millis();
        //digitalWrite(LED2, HIGH);
        //checktime += 200;
        Gear--;
        //delay(1000);
        //digitalWrite(LED2, LOW);
        //Serial.print("Gea1r:");
        //Serial.println(Gear);
        gear_flag=0;
   }
   digitalWrite(LED1, LOW);
   //Serial.print("Gear:");
   //Serial.println(Gear);
   //delay(1000);
   //MsTimer2::start();
   //motorloop(1);
   
}

void Changesetup() {
// initialize the pushbutton pin as an input:
  //Serial.begin(9600);
  pinMode(buttonPin, INPUT); 
  pinMode(buttonPin_2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(buttonPin), changeup, FALLING);
  attachInterrupt(digitalPinToInterrupt(buttonPin_2), changedown, FALLING);
  
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
//  pinMode(LED3, OUTPUT);
}


void Changeloop() {
  // read the state of the pushbutton value:    
     digitalWrite(LED1, LOW);
    /* buttonState = digitalRead(buttonPin);
     buttonState_2 = digitalRead(buttonPin_2);*/
     ChangeT1 = millis();
  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  while(ChangeT2 - ChangeT1 < checktime){
    buttonState = digitalRead(buttonPin);
    buttonState_2 = digitalRead(buttonPin_2);
    digitalWrite(LED1, HIGH);
    ChangeT2 = millis();
    /*if (buttonState == HIGH) {
    checktime += 1000;
      if (Gear<6){
         Gear++;
      }
      else{
        Gear = 5;
      }
      delay(100);
    }
    if (buttonState_2 == HIGH) {
    checktime += 1000;
      if (Gear>1){
        Gear--;
      }
      else{
        Gear = 1;
      }
    }
    delay(100);
  }*/
  if (buttonState == HIGH && Gear<6) {
    digitalWrite(LED2, HIGH);
    checktime += 200;
    Gear++;
    delay(200);
  }
  if (buttonState_2 == HIGH && Gear>1) {
    digitalWrite(LED2, HIGH);
    checktime += 200;
    Gear--;
    delay(200);
  }
  digitalWrite(LED2, LOW);
 }
  digitalWrite(LED1, LOW);
}



