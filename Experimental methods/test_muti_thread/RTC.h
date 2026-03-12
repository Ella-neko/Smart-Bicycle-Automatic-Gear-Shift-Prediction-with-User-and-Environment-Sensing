#include "DS3231.h"
//#include <Wire.h>
//#include "TCA9548.h"

DS3231 Clock;
bool Century=false;
bool h12;
bool PM;
byte ADay, AHour, AMinute, ASecond, ABits;
bool ADy, A12h, Apm;

byte year, month, date, DoW, hour, minute, second;
static String Time = "";
String past_Year = "", past_Month = "", past_Date = "", past_Hour = "", past_Minute = "";
void RTCsetup(int Year,int Month,int Date,int Hour,int Minute,int Second) {
	// Start the I2C interface
	Wire.begin();
  tcaselect(0);
  /*
  Clock.setSecond(Second);//Set the second                          //如果時間跑掉再取消註解進行設定
  Clock.setMinute(Minute);//Set the minute 
  Clock.setHour(Hour);  //Set the hour 
  //Clock.setDoW(1);    //Set the day of the week
  Clock.setDate(Date);  //Set the date of the month
  Clock.setMonth(Month);  //Set the month of the year
  Clock.setYear(Year);  //Set the year (Last two digits of the year)
  */
  /*
  Serial.print("Year : ");
  Serial.println(Year);
  
  Serial.print("Year : ");
  Serial.println(Year);
  Serial.print("Month : ");
  Serial.println(Month);
  Serial.print("Date : ");
  Serial.println(Date);
  Serial.print("Hour : ");
  Serial.println(Hour);
  Serial.print("Minute : ");
  Serial.println(Minute);
  Serial.print("Second : ");
  Serial.println(Second);
  */
  /*past_Year = String(Year);
  past_Month = String(Month);
  past_Date = String(Date);
  past_Hour = String(Hour);
  past_Minute = String(Minute);*/
	//Start the serial interface
	//Serial.begin(9600);
  //delay(1000);
}
//void ReadDS3231()
void RTC_Read()
{
  
  static int second,minute,hour,date,month,year,temperature; 
  second=Clock.getSecond();
  minute=Clock.getMinute();
  hour=Clock.getHour(h12, PM);
  date=Clock.getDate();
  month=Clock.getMonth(Century);
  year=Clock.getYear();
  
  temperature=Clock.getTemperature();
  
  Serial.print("20");
  Serial.print(year,DEC);
  Serial.print('-');
  Serial.print(month,DEC);
  Serial.print('-');
  Serial.print(date,DEC);
  Serial.print(' ');
  Serial.print(hour,DEC);
  Serial.print(':');
  Serial.print(minute,DEC);
  Serial.print(':');
  Serial.print(second,DEC);
  Serial.print('\n');  
  Serial.print("Temperature=");
  Serial.print(temperature); 
  Serial.print('\n');
  //delay(1000);
  //Time = "20" + (String)year + '-' + (String)month + '-' + (String)date + ' ' + (String)hour + ':' + (String)minute + ':' + (String)second;
  Time = "20" + String(year) + '-' + String(month) + '-' + String(date) + ' ' + String(hour) + ':' + String(minute) + ':' + String(second);
  //Serial.print("Time : ");
  //Serial.println(Time);
  /*Serial.print("Temperature=");
  Serial.print(temperature); 
  Serial.print('\n');*/
}
//void loop() {ReadDS3231();delay(1000);}


