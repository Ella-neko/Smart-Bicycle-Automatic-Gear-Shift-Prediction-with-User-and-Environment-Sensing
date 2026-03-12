#include "TinyGPS++.h"
#include <SoftwareSerial.h>
/*This sample sketch demonstrates the normal use of a TinyGPS++ (TinyGPSPlus) object.   
It requires the use of SoftwareSerial, and assumes that you have a 9600-baud serial 
GPS device hooked up on pins 8(rx) and 9(tx).*/
//static const int RXPin = 4, TXPin = 3;
static const uint32_t GPSBaud = 9600;
int gps_flag=0;
String gps_year = "";
String get_year = "";
String gps_month = "";
String gps_date = "";
String gps_hour = "";
String get_hour = "";
String gps_minute = "";
String gps_second = "";
// The TinyGPS++ object
TinyGPSPlus gps;

// The serial connection to the GPS device
//SoftwareSerial ss(RXPin, TXPin);

void GPSsetup()
{
  Serial.begin(9600);
  Serial2.begin(GPSBaud);   //Rx = Rx3(Digital 15)  Tx = Tx3(Digital 14)
  Serial.println("GPS Setup.");
  /*Serial.println(F("DeviceExample.ino"));
  Serial.println(F("A simple demonstration of TinyGPS++ with an attached GPS module"));
  Serial.print(F("Testing TinyGPS++ library v. ")); Serial.println(TinyGPSPlus::libraryVersion());
  Serial.println(F("by Mikal Hart"));
  Serial.println(F("Edited By www.maxphi.com"));
  Serial.println();*/
}
void GPSloop()
{
  //Serial3.begin(GPSBaud);
  while (Serial2.available() > 0){
    gps.encode(Serial2.read());
    if (gps.location.isUpdated()){
      Serial.print("Latitude= "); 
      Serial.print(gps.location.lat(), 6);
      Serial.print(" Longitude= "); 
      Serial.println(gps.location.lng(), 6);
      //Serial.print("Date_Time= ");
      get_year = gps.date.year();
      gps_year = get_year.toInt() - 2000;
      gps_month = gps.date.month();
      gps_date = gps.date.day();
      get_hour = gps.time.hour();
      gps_hour = 8 + get_hour.toInt();
      gps_minute = gps.time.minute();
      gps_second = gps.time.second();
      /*Serial.println(gps_year);
      Serial.println(gps_month);
      Serial.println(gps_date);
      Serial.println(gps_hour);
      Serial.println(gps_minute);
      Serial.println(gps_second);*/
      /*Serial.print("20"+gps.date.year()); // Year
      Serial.print(gps.date.month()); // Month
      Serial.print(gps.date.day()); // Day
      Serial.print(String(int(gps.time.hour())+8)); // Hour Taiwan��+8
      Serial.print(gps.time.minute()); // Minute
      Serial.println(gps.time.second()); // Second */
      gps_flag = 1;
      //Serial3.end();
    }
  }
}



