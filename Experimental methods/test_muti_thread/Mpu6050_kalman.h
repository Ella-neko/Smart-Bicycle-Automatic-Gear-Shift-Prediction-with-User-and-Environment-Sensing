 // Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#include "Wire.h"
 
// I2Cdev and MPU6050 must be installed as libraries, or else the .cpp/.h files
// for both classes must be in the include path of your project
#include "I2Cdev.h"
#include "MPU6050.h"
#include "ArduinoSort.h"
// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69
MPU6050 accelgyro;
 
int16_t ax, ay, az;
int16_t gx, gy, gz;
double total_angle=0;
int angle_num = 0;
float final_Angle = 0;
float Angle_arr[5] = {};
int systemTime_Flag = 0;
/*static*/ unsigned long pretime=0;
#define LED_PIN 13
 
/* 把mpu6050放在水平桌面上，分别读取读取2000次，然后求平均值 */
#define AY_ZERO (0) /* 加速度计的0偏修正值 */
#define GZ_ZERO (0) /* 陀螺仪的0偏修正值 */

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
    accelgyro.setFullScaleGyroRange(3);
    accelgyro.setFullScaleAccelRange(3);
    /*
      * AFS_SEL 0 = 16384 (+-2G)
      * AFS_SEL 1 = 8192  (+-4G)
      * AFS_SEL 2 = 4096  (+-8G)
      * AFS_SEL 3 = 2048  (+-16G)
      * 震動越大AFS_SEL越大
    */
    // verify connection
   // Serial.println("Testing device connections...");
   // Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

    // configure Arduino LED for
    //pinMode(LED_PIN, OUTPUT);
}
 
/* Kalman filter 後最終角度 */
float Angle=0.0; 
 
/*由角速度计算的傾斜角度 */
float Angle_gy=0.0; 
 
float Q_angle=0.001;  
float Q_gyro=0.004;
float R_angle=0.5;
float dt=0.1;        /* dt為kalman濾波器採樣時間; */
char  C_0 = 1;
float Q_bias, Angle_err;
float PCt_0=0.0, PCt_1=0.0, E=0.0;
float K_0=0.0, K_1=0.0, t_0=0.0, t_1=0.0;
float Pdot[4] ={0,0,0,0};
float PP[2][2] = { { 1, 0 },{ 0, 1 } };

void Kalman_Filter(float Accel,float Gyro)                
{
        Angle+=(Gyro - Q_bias) * dt; 
 
        Pdot[0]=Q_angle - PP[0][1] - PP[1][0]; 
        //Serial.println("PP[0][1]"+String(PP[0][1]));
        //Serial.println("PP[1][0]"+String(PP[1][0]));

        Pdot[1]=- PP[1][1];
        Pdot[2]=- PP[1][1];
        Pdot[3]=Q_gyro;
        
        PP[0][0] += Pdot[0] * dt;
        PP[0][1] += Pdot[1] * dt;
        PP[1][0] += Pdot[2] * dt;
        PP[1][1] += Pdot[3] * dt;

        //Serial.println("Angle"+String(Angle));
        Angle_err = Accel - Angle;

        PCt_0 = C_0 * PP[0][0];
        PCt_1 = C_0 * PP[1][0];

        //Serial.println("PCt_0"+String(PCt_0));
        E = R_angle + C_0 * PCt_0;
        //Serial.print("E");
        //Serial.println(E);
        //Serial.println("E"+String(E));
        if(E!=0)
        {
          K_0 = PCt_0 / E;
          K_1 = PCt_1 / E;
        }
        //Serial.println("K_0"+String(K_0));
        t_0 = PCt_0;
        t_1 = C_0 * PP[0][1];
 
        PP[0][0] -= K_0 * t_0;
        PP[0][1] -= K_0 * t_1;
        PP[1][0] -= K_1 * t_0;
        PP[1][1] -= K_1 * t_1;
        Angle        += K_0 * Angle_err;
        Q_bias        += K_1 * Angle_err;
}
 
void gyroloop(int system_flag) {
    //Serial.println("gyro kal");
    //tcaselect(2);
    // read raw accel/gyro measurements from device
    final_Angle = 0;
    angle_num = 0;
    double ay_angle=0.0;
    double gz_angle=0.0;
    unsigned long time=0;
    unsigned long mictime=0;
    if(system_flag == 0){
         pretime=0;
         Angle = 0.0;
         Angle_gy = 0.0;
         Q_bias = 0;
         Angle_err = 0;
         PCt_0=0.0, PCt_1=0.0, E=0.0;
         K_0=0.0, K_1=0.0, t_0=0.0, t_1=0.0;
         float Pdot[4] ={0,0,0,0};
         float PP[2][2] = { { 1, 0 },{ 0, 1 } };
    }
    
    float gyro=0.0;
    
    //if(systemTime_Flag == 0)
    if(pretime==0)
    {
        pretime=millis();
        return;
    }
    mictime=millis();
    
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
 
/* 加速度量程范围设置2g 16384 LSB/g
* 计算公式：
* 前边已经推导过这里再列出来一次
* x是小车倾斜的角度,y是加速度计读出的值
* sinx = 0.92*3.14*x/180 = y/16384
* x=180*y/(0.92*3.14*16384)=
*/
    //Serial.println(ay);
    ay -= AY_ZERO;
    //ay_angle=ay/262;// 0
    //ay_angle=ay/131;// 1
    //ay_angle=ay/66;// 2
    ay_angle=ay/33;// 3
   
/* 陀螺仪量程范围设置250 131 LSB//s 
* 陀螺仪角度计算公式:
* 小车倾斜角度是gx_angle,陀螺仪读数是y,时间是dt
* gx_angle +=(y/(131*1000))*dt 
*/
    gz -= GZ_ZERO;
    time=mictime-pretime;
    gyro=gz/131.0;
    gz_angle=gyro*time;
    //Serial.println("gz_angle"+String(gz_angle));
    gz_angle=gz_angle/1000.0;
    total_angle-=gz_angle;
    //Serial.println("total_angle"+String(total_angle));
    
    dt=time/1000.0;
    Kalman_Filter(ay_angle,gyro);

    /*取5筆檢測結果取平均為最終角度*/
    /*if(angle_num == 5){
      //sortArray(Angle_arr,10);
     // Angle = (Angle_arr[0] + Angle_arr[9]) / 2;
     for(int k = 0;k < 5;k++){
      final_Angle = final_Angle + Angle_arr[k];
     }
     //Angle = final_Angle / 5;//取平均做輸出(mean filter)
     sortArray(Angle_arr,5);
     Angle = Angle_arr[2];//取中值做輸出(median filter)
      //Serial.print(ay_angle); Serial.print(",");
      //Serial.print(total_angle); Serial.print(",");
      //Serial.println(Angle);
    }
    else{
      Angle_arr[angle_num] = Angle;
      angle_num += 1;
    }*/
    //Serial.print(ay_angle); Serial.print(",");
    //Serial.print(total_angle); Serial.print(",");
    //sSerial.println(Angle);
    pretime=mictime;
    //pretime = system_time;
   // Serial.println("pretime_2 = " + String(pretime));
}
