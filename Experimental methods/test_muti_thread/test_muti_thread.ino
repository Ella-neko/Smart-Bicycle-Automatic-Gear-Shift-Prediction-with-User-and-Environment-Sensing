#include <pt.h>
#include <Wire.h>
#include "TCA9548.h"
#include "Heartbeat.h"
//#include "button.h"
#include "motor.h"
#include "weight.h"
#include "Hall.h"
/*#include "MPU6050_raw.h"*/
#include "Mpu6050_kalman.h"
#include "mode.h"
#include "RTC.h"
#include "GPS.h"
#include "Manual_change_gear.h"
#include "SD_Card.h"
#include <avr/pgmspace.h>


#define TEMP_PIN A4


int InterNet_state = 0/*, Receive_state = 0*/;//確認網路狀態 1 = 已連線，2 = 未連線 //確認Raspberry Pi接收資料//
float Slope=0, beat = 0,RPM = 0,NPressure = 0;
float beat_arr[5] = {}, Pressure_arr[10] = {};
String check_year = "";
String s = "";
//String upload = "";
//byte slave_address = 0x04;
int check = 0,check_flag = 0/*,upLoad = 0, upLoad_flag = 0*/;
int off_line_data = 0;//用來確認sd卡內資料以上傳
unsigned long systemTime = 0;
float median_Angle[5] = {};
String past_Lat = "";
String past_Lng = "";
/*
 小寫upload為儲存Sensor之字串資料
 大寫upLoad為控制上傳至RaspBerry Pi之Flag之一
 */
/*
 註解掉之變數定義於SD_Card.h中
 下方Sent Sensor Data to Raspberry Pi
 也定義於SD_Card.h
 */

 unsigned long R_time;
 unsigned long P_time;
 unsigned long S_time;
 unsigned long H_time;
 unsigned long Ge_time;
 unsigned long Te_time;
/*↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓----------------------------Check Raspberry Pi Internet State-----------------------------↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓*/
void Net_check(String SENT) {  
  //Serial.begin(9600);
  s = SENT;
  //Serial.println("1");
  Wire.begin(slave_address);
  //Serial.println("2");
  tcaselect(1);
  //Serial.println("3");
  Wire.onReceive(receiveEvent);//從機 接收 主機 發來的數據
  Wire.onRequest(sendData); //從機 請求 主機 發送數據
  Serial.println("Ready to receive Raspberry Pi data.");
}
void receiveEvent(int howMany) {
  int numOfBytes = Wire.available();
  byte b = Wire.read();  //cmd
  char results[] = {};
  //char empty[] = {""};
  //Serial.println(sizeof(results));
  for(int i=0; i<=numOfBytes-2; i++){
    char data = Wire.read();
    results[i] = data;
    //Serial.print(data);
    if (String(data) == "1"){
      Serial.println("已上網");
      InterNet_state = 1;
    }
    if (String(data) == "2"){
      InterNet_state = 2;
      Serial.println("未連線");
    }
  }
  //Serial.print("Receive:");
  //Serial.println(String(results));
  for(int i=0; i<=numOfBytes-2; i++){
    results[i] = "\0";
  }
  //Serial.print("Receive:");
  //Serial.println(results);
  Serial.println("\t");//一定要多這行否則array無法清除
}
void sendData(){
  char buffer[32];
  s.toCharArray(buffer, 32);
  Wire.write(buffer);
 }
/*↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑----------------------------Check Raspberry Pi Internet State-----------------------------↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑*/

/*↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓----------------------------Sent Sensor Data to Raspberry Pi-----------------------------↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓*/
/*
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
void send_sensor_Data(){
  char buffer[32];
  upload.toCharArray(buffer, 32);
  Wire.write(buffer);
 }
 void receive_signal(int howMany) {
  int numOfBytes = Wire.available();
  byte b = Wire.read();  //cmd
  char results[] = {};
  //char empty[] = {""};
  //Serial.println(sizeof(results));
  for(int i=0; i<=numOfBytes-2; i++){
    char data = Wire.read();
    results[i] = data;
    //Serial.print(data);
    if (String(data) == "1"){
      Serial.println("已收到");
      Receive_state = 1;
    }
    if (String(data) == "2"){
      Receive_state = 2;
      Serial.println("未收到");
    }
  }
  //Serial.print("Receive:");
  //Serial.println(String(results));
  for(int i=0; i<=numOfBytes-2; i++){
    results[i] = "\0";
  }
  //Serial.print("Receive:");
  //Serial.println(results);
  Serial.println("\t");//一定要多這行否則array無法清除
}
*/
/*↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑----------------------------Sent Sensor Data to Raspberry Pi-----------------------------↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑*/
/*Sent Sensor Data to Raspberry Pi定義於SD.h中*/
void Slope_func()
{  
   //Serial.println("Slope 0 ");
   sei();
   tcaselect(2);
   gyroloop(1);
   Slope = Angle;
   //Serial.println("Slope = " + String(Slope));//must be add.
   sei();
}

static struct pt ptRPM, ptPress, ptGyro, ptSubGyro, ptHeart, ptGear, ptTemp, ptMotor;

static int protothreadMotor(struct pt *pt){
  static unsigned long lastTimeBlinkMotor = 0;
  PT_BEGIN(pt);
  while(1) {
    lastTimeBlinkMotor = millis();
    PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkMotor > 300);
    //MsTimer2::stop( );
    motorloop(Gear);
    gear_flag=1;
    //MsTimer2::start( );
  }
  PT_END(pt);
}

static int protothreadSubGyro(struct pt *pt){
  static unsigned long lastTimeBlinkSubGyro = 0;
  PT_BEGIN(pt);
  while(1) {
    lastTimeBlinkSubGyro = millis();
    PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkSubGyro > 10);
    //sei();
    
    tcaselect(2);
    gyroloop(1);
    Slope = Angle;
    //Serial.println("Slope = " + String(Slope));//must be add.
    //cli();
  }
  PT_END(pt);
}

static int protothreadRPM(struct pt *pt)
{
  
  static unsigned long lastTimeBlinkRPM = 0;
  PT_BEGIN(pt);
  while(1) {
    lastTimeBlinkRPM = millis();
    
    PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkRPM > 1);
    //MsTimer2::stop( );
    hallloop();
    RPM = rate;
    
    //R_time=R_time/100;
    //SDloop("haGy"+String(Slope)+";"+String(S_time)+","+"haH"+String(int(beat))+";"+String(H_time)+"haR"+String(RPM,2)+";"+String(R_time)+","+"haP"+String(NPressure)+";"+String(P_time)+"haTe" + String(Temp)+";"+String(Te_time)+","+"haGe"+String(Gear)+";"+String(Ge_time)+","+"haLat");
    if(RPM <= 100.0 && RPM > 0){
      R_time=millis();
      SDloop("haR"+String(RPM,2)+";"+String(R_time));
      rate=0;
    }
    //MsTimer2::start( );
    //Serial.println("haR"+String(RPM,2));
  }
  PT_END(pt);
  
}

static int protothreadPress(struct pt *pt)
{
  
  static unsigned long lastTimeBlinkPress = 0;
  PT_BEGIN(pt);
  while(1) {
    lastTimeBlinkPress = millis();
    
    PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkPress > 100);
    //MsTimer2::stop( );
    prloop();
    NPressure = Kilogram;
    P_time=millis();
    //P_time=P_time/100;
    //SDloop("haGy"+String(Slope)+";"+String(S_time)+","+"haH"+String(int(beat))+";"+String(H_time)+"haR"+String(RPM,2)+";"+String(R_time)+","+"haP"+String(NPressure)+";"+String(P_time)+"haTe" + String(Temp)+";"+String(Te_time)+","+"haGe"+String(Gear)+";"+String(Ge_time)+","+"haLat");
    if(NPressure > 0.05){
      SDloop("haP"+String(NPressure)+";"+String(P_time));
    }
    
    //Serial.print("haP"+String(NPressure)+";"+String(P_time));
    //Serial.print('\n');
    
    //MsTimer2::start( );
  }
  PT_END(pt);
  
}

static int protothreadGyro(struct pt *pt)
{
  //
  static unsigned long lastTimeBlinkGyro = 0;
  PT_BEGIN(pt);
  while(1) {
    lastTimeBlinkGyro = millis();
    
    PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkGyro > 200);
    //MsTimer2::stop( );
    //Serial.println(Slope);
    //S_time=millis();
    S_time=millis();
    //SDloop("haGy"+String(Slope)+";"+String(S_time)+","+"haH"+String(int(beat))+";"+String(H_time)+"haR"+String(RPM,2)+";"+String(R_time)+","+"haP"+String(NPressure)+";"+String(P_time)+"haTe" + String(Temp)+";"+String(Te_time)+","+"haGe"+String(Gear)+";"+String(Ge_time)+","+"haLat");
    SDloop("haGy"+String(Slope)+";"+String(S_time));
    
    Serial.print("haGy"+String(Slope)+";"+String(S_time));
    Serial.print('\n');
    
    //MsTimer2::start( );
  }
  PT_END(pt);
  
}

static int protothreadHeart(struct pt *pt)
{
  static unsigned long lastTimeBlinkHeart = 0;
  PT_BEGIN(pt);
  while(1) {
    lastTimeBlinkHeart = millis();
    
    PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkHeart > 200);
    //MsTimer2::stop( );
    for (int i = 0;i<10;i++){
      beatloop();
      beat = currentHeartrate / 3;
    }
    H_time=millis();
    //SDloop("haGy"+String(Slope)+";"+String(S_time)+","+"haH"+String(int(beat))+";"+String(H_time)+"haR"+String(RPM,2)+";"+String(R_time)+","+"haP"+String(NPressure)+";"+String(P_time)+"haTe" + String(Temp)+";"+String(Te_time)+","+"haGe"+String(Gear)+";"+String(Ge_time)+","+"haLat");
    SDloop("haH"+String(int(beat))+";"+String(H_time));
    
    //Serial.print("haH"+String(int(beat))+";"+String(H_time));
    //Serial.print('\n');
    
    //MsTimer2::start( );
  }
  PT_END(pt);
}

static int protothreadGear(struct pt *pt)
{
  
  static unsigned long lastTimeBlinkGear = 0;
  PT_BEGIN(pt);
  RTC_Read();
  Ge_time=millis();
  SDloop("Time"+String(Time)+";"+String(Ge_time));
  while(1) {
    lastTimeBlinkGear = millis();
    
    PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkGear > 200);
    //MsTimer2::stop( );
    Ge_time=millis();
    //RTCsetup(21,04,12,14,35,00);
    //
    
    //SDloop("haGy"+String(Slope)+";"+String(S_time)+","+"haH"+String(int(beat))+";"+String(H_time)+"haR"+String(RPM,2)+";"+String(R_time)+","+"haP"+String(NPressure)+";"+String(P_time)+"haTe" + String(Temp)+";"+String(Te_time)+","+"haGe"+String(Gear)+";"+String(Ge_time)+","+"haLat");
    SDloop("haGe"+String(Gear)+";"+String(Ge_time));
    /*
    Serial.print("haGe"+String(Gear)+";"+String(Ge_time));
    Serial.print('\n');
    */
    //MsTimer2::start( );
  }
  PT_END(pt);
  
}

static int protothreadTemp(struct pt *pt)
{
  
  static unsigned long lastTimeBlinkTemp = 0;
  PT_BEGIN(pt);
  while(1) {
    lastTimeBlinkTemp = millis();
    
    PT_WAIT_UNTIL(pt, millis() - lastTimeBlinkTemp > 200);
    //MsTimer2::stop( );
    int temp_raw = analogRead(TEMP_PIN);  //从A4讀取類比訊號，值介於0~1024之間
    double Temp;
    Temp = log(10000.0 / (1024.0 / temp_raw - 1));
    Temp = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * Temp * Temp ))* Temp );
    Temp = Temp-273.15;
    Te_time=millis();
    //SDloop("haGy"+String(Slope)+";"+String(S_time)+","+"haH"+String(int(beat))+";"+String(H_time)+"haR"+String(RPM,2)+";"+String(R_time)+","+"haP"+String(NPressure)+";"+String(P_time)+"haTe" + String(Temp)+";"+String(Te_time)+","+"haGe"+String(Gear)+";"+String(Ge_time)+","+"haLat");
    SDloop("haTe" + String(Temp)+";"+String(Te_time));
    /*
    Serial.print("haTe" + String(Temp)+";"+String(Te_time));
    Serial.print('\n');
    */
    //MsTimer2::start( );
  }
  PT_END(pt);
  
}

void setup() {
   
  Serial.begin(9600); 
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  digitalWrite(13, LOW);
 /* GPSsetup();
  while(gps_flag==0){//直到GPS接收到訊號前不斷重複
    digitalWrite(13, HIGH);
    GPSloop();
  }
  Serial3.end();*/
  digitalWrite(13, LOW);
  Serial.println("0");
  
  while(Slope == 0){
    gyro();
    tcaselect(2);
    gyroloop(0);
    tcaselect(2);
    gyroloop(1);
    Slope = Angle;
    //Slope = 1;
    Serial.println(Slope);
    delay(500);
  }
  Serial.println("1.9");
  //MsTimer2::set(10, Slope_func);//每10ms測一次Gyro
  
  
  Serial.print("1");
  //RTCsetup(gps_year.toInt(),gps_month.toInt(),gps_date.toInt(),gps_hour.toInt(),gps_minute.toInt(),gps_second.toInt()); 
  RTCsetup(21,04,14,11,57,10);
  
  Serial.print("2");
  Heartbeat();
  Serial.print("3");
  Hall();
  Serial.print("4");
  Pressure();
  Serial.print("5");
  motorsetup();
  Serial.print("6");
  Changesetup();
  Serial.print("7");
  
  SDsetup();
  Serial.print("8");
  
  //PT_INIT(&ptRPM);
  PT_INIT(&ptPress);
  PT_INIT(&ptGyro);
  PT_INIT(&ptSubGyro);
  PT_INIT(&ptHeart);
  PT_INIT(&ptGear);
  PT_INIT(&ptTemp);
  PT_INIT(&ptMotor);
  Serial.print("9");
  //MsTimer2::start( );
}

void(* resetFunc) (void) = 0;

void loop(){
  //MsTimer2::stop( );
  //MsTimer2::start( );
  
  protothreadSubGyro(&ptSubGyro);
  //protothreadRPM(&ptRPM);
  protothreadPress(&ptPress);
  protothreadHeart(&ptHeart);
  protothreadGear(&ptGear);
  protothreadTemp(&ptTemp);
  protothreadGyro(&ptGyro);
  protothreadMotor(&ptMotor);
  
  //Slope=-5/0.0;
  if(isnan(Slope)){
      //Serial.print("NAN");
      resetFunc();
  }
  
  /*
  hallloop();
  RPM = rate;
  R_time=millis();
  if(RPM <= 100.0 && RPM > 0){
      SDloop("haR"+String(RPM,2)+";"+String(R_time));
  }
  Serial.println("haR"+String(RPM,2)+";"+String(R_time));
  */
  //RTCsetup(21,04,12,15,35,25);

  //MsTimer2::stop( );
  /*
  motorloop(Gear);
  gear_flag=1;
  */
  //MsTimer2::start( );
}


