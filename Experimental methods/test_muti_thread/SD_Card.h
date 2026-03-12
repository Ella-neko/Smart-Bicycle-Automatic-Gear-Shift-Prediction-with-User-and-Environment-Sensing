/*
 *  Arduino SD Card Tutorial Example
 *  
 *  by Dejan Nedelkovski, www.HowToMechatronics.com
 */
//https://howtomechatronics.com/tutorials/arduino/arduino-sd-card-data-logging-excel-tutorial/
#include <SD.h>
#include <SPI.h>
//#include "wifi.h"
#include "MsTimer2.h"

File myFile;
int upLoad_flag = 0, Receive_state = 0, upLoad = 0; 
String upload = "";
int pinCS = 53; // Pin 53 on Arduino
byte slave_address = 0x04;

/*↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓----------------------------Sent Sensor Data to Raspberry Pi-----------------------------↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓*/
void send_sensor_Data(){
  char buffer[32];
  upload.toCharArray(buffer, 32);
  Wire.write(buffer);
 }
 void receive_signal(int howMany) {
  MsTimer2::stop();
  int numOfBytes = Wire.available();
  byte b = Wire.read();  //cmd
  String rec_data = "";
  //char empty[] = {""};
  //Serial.println(sizeof(results));
  for(int i=0; i<=numOfBytes-2; i++){
    char data = Wire.read();
    rec_data = rec_data + String(data);
    delay(100);
  }
  if(rec_data == "1"){
    Serial.println("已收到");
    Receive_state = 1;
  }
  if(rec_data == "2"){
    Serial.println("未收到");
    Receive_state = 2;
  }
  if(rec_data[0] == 'G'){
    Serial.print("隨機森林換檔資料 = ");
    Serial.println(String(rec_data[1]) + "檔");
    Gear = String(rec_data[1]).toInt();
    Receive_state = 3;
  }
}

void upLoad_data(String sensor_data) {  
  //Serial.begin(9600);
  upload = sensor_data;
  //Serial.println("1");
  Wire.begin(slave_address);
  //Serial.println("2");
  tcaselect(1);
  //Serial.println("3");
  
  Wire.onRequest(send_sensor_Data); //從機 請求 主機 發送數據
  Wire.onReceive(receive_signal);//從機 接收 主機 發來的數據
  //Serial.println("Ready to receive Raspberry Pi data.");
}
/*↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑----------------------------Sent Sensor Data to Raspberry Pi-----------------------------↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑*/

void SDsetup() {
    
 // Serial.begin(9600);
  pinMode(pinCS, OUTPUT);
  digitalWrite(pinCS, HIGH);
  // SD Card Initialization
  
  if (SD.begin())
  {
    Serial.println("SD card is ready to use.");
    digitalWrite(6, LOW);
    //SD.remove("test.txt");
    //Serial.println("test.txt has been remove.");
    delay(5000);
  } else
  {
    Serial.println("SD card initialization failed");
    digitalWrite(6, HIGH);
    digitalWrite(7, LOW);
    delay(500);
    digitalWrite(7, HIGH);
    digitalWrite(6, LOW);
    delay(500);
    SDsetup();
  }
  
}
void SD_read(){
  MsTimer2::stop();
  Serial.println("Read_SD Card.");
  myFile = SD.open("test.txt");
  if (myFile) {
    Serial.println("Read:");
    // Reading the whole file
    String txt_data = myFile.readStringUntil('\n');
    while (txt_data!="") {
      //Serial.write(myFile.read());
      //String data_cate = myFile.readStringUntil(',');
      txt_data = myFile.readStringUntil('\n');
      Serial.println("SD_Card_data:" /*+ data_cate*/ + txt_data);
      
      upLoad_flag = 0;
      Receive_state = 0;
      if(upLoad_flag == 0 && txt_data!=""){
        upLoad_data(txt_data);
        upLoad_flag = 1;
        upLoad = 1;
      }
      
      Serial.print("Receive_state 2: ");
      Serial.println(Receive_state);
      Serial.print("upLoad: ");
      Serial.println(upLoad);
      while(upLoad == 1 || Receive_state == 0){
          upLoad = 0;
          Serial.print("upLoad ");
          Serial.print("Receive_state 3: ");
          Serial.println(Receive_state);
          switch(Receive_state){
            case 0:
              Serial.println("Raspberry Pi 尚未接收SD_Card資料");
              break;
          }
          delay(2000);
      }

      
      //wifiloop(data_cate , txt_data);
   }
    myFile.close();
    SD.remove("test.txt");
    MsTimer2::start();
  }
}
void SDloop(String(store_data)) {   //資料
    // Create/Open file

    myFile = SD.open("test.txt", FILE_WRITE);
   
  // if the file opened okay, write to it:
  if (myFile) {
    SD_gear_flag2=1;
    //Serial.println("Writing to file...");
    // Write to file
      myFile.print(store_data+'\n');
    //myFile.close(); // close the file
    //Serial.println("Done.");
  }
  // if the file didn't open, print an error:
  else {
    SD_gear_flag2=0;
    Serial.println("error opening test.txt");
  }
    myFile.close();

     // Reading the file
    //SD_read();
 /* else {
    Serial.println("error opening test.txt");
  }*/
}

