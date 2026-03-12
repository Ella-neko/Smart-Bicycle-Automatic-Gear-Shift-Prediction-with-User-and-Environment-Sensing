#include "HX711.h"
float Weight = 0;
int Sec_Count = 0;
int Status = 0,Status_Pre = 1;
int Flag_Up = 0,Flag_Down = 0;
float Kilogram=0;

void Pressure()
{
	Init_Hx711();				//初始化HX711模組連接的IO設置
 //Serial.println("666");
	//Serial.begin(9600);
	//Serial.println("Pressure Ready!");
        Get_Maopi();		//獲取毛皮
        //Serial.println("777");
	delay(3000);
      	Get_Maopi();		//獲取毛皮
        //Serial.println("888");
}

void prloop()
{
	Weight = Get_Weight();	//計算放在感測器上的重物重量
        
        if(Weight <= 5)
        {
          Status = 0;       
        }
        else
        {
          Status = 1;		
        }
          
        if(Status != Status_Pre)
        {
          if(Status == 1 && Status_Pre == 0)		
          {
            Flag_Up = 1;
          }
          if(Status == 0 && Status_Pre == 1)		
          {
            Flag_Down = 1;
          }
          Status_Pre = Status;         
        }
        
        if(Flag_Up == 1)				
        {
          Flag_Up = 0;
          Sec_Count = 0;
        }
        
        if(Status == 1 || Flag_Down == 1)		
        {
          Flag_Down = 0;
          Kilogram = Weight/1000;
          if(Kilogram<66&&Kilogram>56)
             Kilogram = 0;
          /*  Serial.print("0.00");	//串口顯示重量
          else
              Serial.print(Kilogram);
          Serial.print(Weight);
      	  Serial.print("Kg ");	  //顯示單位
          if(Status == 1)
            Serial.print(++Sec_Count);
          else
            Serial.print(Sec_Count);
          Serial.print("ms\n");*/
        }
        
        
        
//	delay(100);				//延時0.1s
}

