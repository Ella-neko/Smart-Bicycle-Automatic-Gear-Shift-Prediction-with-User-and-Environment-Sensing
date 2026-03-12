// I2C device class (I2Cdev) demonstration Arduino sketch for MPU6050 class
// 10/7/2011 by Jeff Rowberg <jeff@rowberg.net>
// Updates should (hopefully) always be available at https://github.com/jrowberg/i2cdevlib
//
// Changelog:
//     2011-10-07 - initial release

/* ============================================
I2Cdev device library code is placed under the MIT license
Copyright (c) 2011 Jeff Rowberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================
*/

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#include "Wire.h"

// I2Cdev and MPU6050 must be installed as libraries, or else the .cpp/.h files
// for both classes must be in the include path of your project
#include "I2Cdev.h"
#include "MPU6050.h"
#include "ArduinoSort.h"
//#include "RTC.h"//-----------------------------------------------------時間模組
// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69
MPU6050 accelgyro;

int16_t ax, ay, az;
int16_t gx, gy, gz;

#define LED_PIN 13
bool blinkState = false;
float res = 0;
float res_arr[10];
float final_res = 0;    
float Total = 0, Mean = 0, Sigma = 0, Minus = 0;//Minus是Xi減去平均值後的平方    
void gyro() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    Wire.begin();
    // initialize serial communication
    // (38400 chosen because it works as well at 8MHz as it does at 16MHz, but
    // it's really up to you depending on your project)
    //Serial.begin(38400);

    // initialize device
   // Serial.println("Initializing I2C devices...");
    accelgyro.initialize();
    
    // verify connection
   // Serial.println("Testing device connections...");
   // Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

    // configure Arduino LED for
    //pinMode(LED_PIN, OUTPUT);
}

short MPU6050_Get_Angle(float x,float y,float z,u8 dir)
{
  float temp;
  switch(dir)
  {
          case 0://與Z軸夾角
                  temp=sqrt((x*x+y*y))/z;
                  res=atan(temp);
                  break;
          case 1://與X軸夾角
                  temp=x/sqrt((y*y+z*z));
                  res=atan(temp);
                  break;
          case 2://與Y軸夾角
                  temp=y/sqrt((x*x+z*z));
                  res=atan(temp);
                  break;
  }
  return res*180/3.14;//弧度轉角度
}

void gyroloop() {
    Serial.println("gyro raw");
    Total = 0;
    Mean = 0;
    Sigma = 0;
    Minus = 0;
    final_res = 0;
    //tcaselect(2);
    //Serial.println("Gyro");
    //for (int i = 0; i < 10; i++){
    // read raw accel/gyro measurements from device
      accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    /*MPU6050_Get_Angle(ax,ay,az,0);
    Serial.print("Z頠�: ");
    Serial.println(res);
    MPU6050_Get_Angle(ax,ay,az,1);
    Serial.print("X頠�: ");
    Serial.println(res);*/
      MPU6050_Get_Angle(ax,ay,az,2);
    //Serial.print("Y頠�: ");
    //Serial.println(res);
      /*res_arr[i] = res;
      Serial.println("第" + String(i) + "筆 = " + String(res));*/
      //final_res = final_res + res / 10 ;
    //}
    /*計算標準差*/
    /*for (int n = 0;n <10; n++){
      Total = Total + res_arr[n];
      //Serial.println("Total = " + String(Total));
    }
    Mean = Total / 10;
    Serial.println("Mean = " + String(Mean));
    for (int n = 0;n <10; n++){
      Minus = Minus + pow((res_arr[n] - Mean),2);
    }
    Sigma = sqrt(Minus / 10);
    Serial.println("Sigma = " + String(Sigma));
    if(Sigma < 0.1 ){
      sortArray(res_arr,10);
      final_res = (res_arr[5] + res_arr[6]) / 2;          //測10次後取中間值 避免雜訊
    }
    else{
      Serial.println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
      gyroloop();
    }*/
    /*Serial.print("Before Sort: ");
    for(int i = 0; i < 10; i++)
    {
      Serial.print(res_arr[i]);
      Serial.print(" ");
    }
    Serial.println("");
    
    Serial.print("After Sort: ");
    for(int i = 0; i < 10; i++)
    {
      Serial.print(res_arr[i]);
      Serial.print(" ");
    }
    Serial.println("");*/
}

