#include "hx711.h"
      

long HX711_Buffer = 0;
long Weight_Maopi = 0,Weight_Shiwu = 0;

//****************************************************
//****************************************************
void Init_Hx711()
{
	pinMode(HX711_SCK, OUTPUT);	
	pinMode(HX711_DT, INPUT);
}


//****************************************************
//****************************************************
void Get_Maopi()
{
	HX711_Buffer = HX711_Read();
	Weight_Maopi = HX711_Buffer/100;		
} 

//****************************************************
//****************************************************
unsigned int Get_Weight()
{
	HX711_Buffer = HX711_Read();
	HX711_Buffer = HX711_Buffer/100;

	Weight_Shiwu = HX711_Buffer;
	Weight_Shiwu = Weight_Shiwu - Weight_Maopi;				
	
	Weight_Shiwu = (unsigned int)((float)Weight_Shiwu/0.429+0.05); 	


	return Weight_Shiwu;
}

//****************************************************
//****************************************************
unsigned long HX711_Read(void)	
{
	unsigned long count; 
	unsigned char i;
	bool Flag = 0;

	digitalWrite(HX711_DT, HIGH);
	delayMicroseconds(1);

	digitalWrite(HX711_SCK, LOW);
	delayMicroseconds(1);

  	count=0; 
  	while(digitalRead(HX711_DT)); 
  	for(i=0;i<24;i++)
	{ 
	  	digitalWrite(HX711_SCK, HIGH); 
		delayMicroseconds(1);
	  	count=count<<1; 
		digitalWrite(HX711_SCK, LOW); 
		delayMicroseconds(1);
	  	if(digitalRead(HX711_DT))
			count++; 
	} 
 	digitalWrite(HX711_SCK, HIGH); 
	count ^= 0x800000;
	delayMicroseconds(1);
	digitalWrite(HX711_SCK, LOW); 
	delayMicroseconds(1);
	
	return(count);
}


