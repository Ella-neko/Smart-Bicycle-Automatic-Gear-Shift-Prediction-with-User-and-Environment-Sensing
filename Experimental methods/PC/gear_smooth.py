# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

#df = pd.read_csv('data/2021317121841output.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/0330/2021330111326output.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/after_ID/all_data.csv')
#'data/can_Internal_difference/static_IMU/multiprocess/0419/after_pv2.csv'
df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_pv2_3_timesave.csv')
after_smooth = pd.DataFrame()
(row,col)=df.shape

'''
date=np.zeros(row)

for i in range(0,row):
    time=df['pickup_datetime'][i]
    a=time.split(" ")
    a=a[0].split("-")
    date[i]=a[2]
'''

past_gear=df['Gear'][0]
i=0
buffer=pd.DataFrame([[df['lati'][i],df['long'][i],df['Gyro'][i],df['Gear'][i],df['Rate'][i],df['Pressure'][i], df['Heartbeat'][i], df['Temp'][i]]])
after_smooth=pd.concat([after_smooth,buffer], ignore_index=True)
        
for i in range(1,row):
    '''
    stand_time=df['gearTime'][i]
    '''
    #if((abs(df['Gear'][i]-past_gear)>1) and date[i]==date[i-1]):
    if((abs(df['Gear'][i]-past_gear)>1)):
        for j in range(1,int(abs(df['Gear'][i]-past_gear))):
            rate=j/abs(df['Gear'][i]-past_gear)
            print(rate)

            buffer=pd.DataFrame([[(df['lati'][i-1]+(df['lati'][i]-df['lati'][i-1])*rate) \
                                  ,(df['long'][i-1]+(df['long'][i]-df['long'][i-1])*rate) \
                                  ,(df['Gyro'][i-1]+(df['Gyro'][i]-df['Gyro'][i-1])*rate) \
                                  ,(df['Gear'][i-1]+(df['Gear'][i]-df['Gear'][i-1])*rate) \
                                  ,(df['Rate'][i-1]+(df['Rate'][i]-df['Rate'][i-1])*rate) \
                                  ,(df['Pressure'][i-1]+(df['Pressure'][i]-df['Pressure'][i-1])*rate) \
                                  ,(df['Heartbeat'][i-1]+(df['Heartbeat'][i]-df['Heartbeat'][i-1])*rate) \
                                  ,(df['Temp'][i-1]+(df['Temp'][i]-df['Temp'][i-1])*rate)]])
            after_smooth=pd.concat([after_smooth,buffer], ignore_index=True)
            print("zzzzz")
        print("-----------------------------------")
        buffer=pd.DataFrame([[df['lati'][i],df['long'][i],df['Gyro'][i],df['Gear'][i],df['Rate'][i],df['Pressure'][i], df['Heartbeat'][i], df['Temp'][i]]])
        after_smooth=pd.concat([after_smooth,buffer], ignore_index=True)
        #aaa=0
    else:
        buffer=pd.DataFrame([[df['lati'][i],df['long'][i],df['Gyro'][i],df['Gear'][i],df['Rate'][i],df['Pressure'][i], df['Heartbeat'][i], df['Temp'][i]]])
        after_smooth=pd.concat([after_smooth,buffer], ignore_index=True)
    past_gear=df['Gear'][i]        
    #stand_time=df['gearTime'][i]
    #print(stand_time)
    
#df = df[df['Heartbeat'].notna()]
#pickup_datetime,lati,long,Gyro,Gear,Rate,Pressure,Heartbeat,Temp,gearTime,HeartTime,GyroTime,RateTime,PressureTime,TempTime
after_smooth.columns=['lati','long','Gyro','Gear','Rate','Pressure','Heartbeat','Temp']

#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0419/after_pv2.csv')
#after_smooth.to_csv(r'data/can_Internal_difference/static_IMU/after_ID/after_GS.csv', index = False)
after_smooth.to_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_GS_skip_freetime_3.csv', index = False)
