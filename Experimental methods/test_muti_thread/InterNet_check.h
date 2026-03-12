#include <Wire.h>
#include "TCA9548.h"
byte slave_address = 0x04;
void Internet_check(){
  tcaselect(1);
  Wire.beginTransmission(slave_address);
  Wire.write("1");
  Wire.endTransmission();
  Serial.println("1");
  delay(100);
}


