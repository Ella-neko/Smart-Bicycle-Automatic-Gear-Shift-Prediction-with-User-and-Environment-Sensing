
int buttonpin=3; //設定線性霍爾磁力感測器接腳為 D3
int val = 0;//設定變量val
float CF = 208.0;  //26吋輪框週長208公分 
static float startTime;
static float duration;
static float rate = 0.0;
static int index=0, interrupt = 0;

void Hall()
{ 
  //Serial.begin(9600);
  pinMode(buttonpin,INPUT);//設定感測器為輸入
  //Serial.println("Howard Ready");
}


void hallloop()
{
  //int index = 0;
    /*if(index ==-1 ){
    Serial.println("紀錄點");
    }*/
   /*if(index ==0 ){
    Serial.println("開始測速");
    }*/
  Serial.println("index___:"+String(index));
  while(index != 3){
   val = analogRead(buttonpin);//將感測器的值讀给val
   Serial.println(val);
   Serial.println("index:"+String(index));
   /*if(val < 500){
    Serial.println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
    index = 3;
   }*/
    //delay(200);
//  Serial.println(val);
    if(val > 500 && index == 0){
      break;
    }
    if(val < 500 && index == 0){
      index = 1;
      startTime = millis();
    }
    else if(val > 500 && index == 1){
      index = 2;
    }
    else if(val < 500 && index == 2){
      index = 3;
      duration = (millis() - startTime) / 1000.0;
    }
    if (duration == 0.0 && index == 3){
      //hallloop();
      index = 0;
    }
    if(index == 3){
      index = 0;
      rate = CF / float(duration);    // cm / seconds
      rate = rate * 0.036;           // km / hr
      break;
    }
    /*while(val < 500 && index < 2){
      val = analogRead(buttonpin);
      //Serial.println(val);
      index = 1;
      startTime = millis();
    }
    if(index == 1 && val >=500){
      //Serial.println("第一次記錄點");
      index = 2;
    }
    while(val < 500 && index == 2){
      //Serial.println("計算速度:");
      val = analogRead(buttonpin);
      duration = (millis() - startTime) / 1000; //秒
      //Serial.println(duration);
      if(duration == 0){
        hallloop();
      }
      index = 3;
    }
    if(index == 3){
      rate = CF / float(duration);    // cm / seconds
      rate = rate * 0.036;           // km / hr
    }*/
 /*if(val < 500)//當感測器檢测有信号時，LED 閃爍
 {
    index++;
    if(index == 1 ){
      val = analogRead(buttonpin);
      if(val > 500){
        startTime = millis();
        interrupt = 1;
      }
    //Serial.print("Start = ");
    //Serial.println(startTime);
    //delay(2000);
    }
    if(index == 2 && interrupt == 1){
     //Serial.print("End = ");
     //Serial.println(millis());
      duration = (millis() - startTime);
      Serial.println(duration);
      if(duration == 0){
        hallloop();
      }
      rate = CF/duration;
     }
   }*/
  }
}

