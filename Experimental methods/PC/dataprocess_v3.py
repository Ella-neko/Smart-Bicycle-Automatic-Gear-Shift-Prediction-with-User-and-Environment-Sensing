# -*- coding: utf-8 -*-

#會儲存時間的版本
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
#df = pd.read_csv('data/2021317121841output.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0419/2021419101754output.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0419/TEST_0419.TXT')
d = open('data/can_Internal_difference/static_IMU/multiprocess/0609_out/202169175920output_3.csv', 'r')
#2021/4/19 18:43:20 - > rpi 2021/4/19 18:44:36
f = open('data/can_Internal_difference/static_IMU/multiprocess/0609_out/TEST_0609_3.TXT', 'r')

#print(f.readlines())
gps_buffer=d.readlines()
buffer=f.readlines()
'''
tmp=0

while True:
    tmp=tmp+1
    buffer=f.readline()
    #print(tmp)
  '''
  

#print(buffer)
gps=np.zeros((1,5))
data=np.zeros((1,12))
time_data=[]

date=""
gps_collector=np.zeros((1,5))
collector=np.zeros((1,12))
collector_count=8
year='0'
month='0'
date='0'
for i in range(0,len(buffer)):
    tmp=buffer[i].split(';')
    if(tmp[0][0:4]=='Time'):
        
        stand_time=int(tmp[1][:-1])
        tmp=tmp[0].split(' ')
        
        year=tmp[0].split('-')[0]
        year=year.split('e')[1]
        month=tmp[0].split('-')[1]
        date=tmp[0].split('-')[2]
        
        tmp=tmp[1].split(':')
        time_buffer=(int(tmp[0])*3600+int(tmp[1])*60+int(tmp[2]))*1000
        stand_time=time_buffer-stand_time
        print(stand_time)
    elif(tmp[0][0:3]=='haH'):
        collector[0,0]=float(tmp[0][3:])
        collector[0,1]=stand_time+float(tmp[1][:-1])
    elif(tmp[0][0:4]=='haTe'):
        collector[0,2]=float(tmp[0][4:])
        collector[0,3]=stand_time+float(tmp[1][:-1])
    elif(tmp[0][0:4]=='haGy'):
        collector[0,4]=float(tmp[0][4:])
        collector[0,5]=stand_time+float(tmp[1][:-1])
    elif(tmp[0][0:3]=='haP'):
        collector[0,collector_count]=float(tmp[0][3:])
        collector[0,collector_count+1]=stand_time+float(tmp[1][:-1]) 
        if(collector_count==8):
            collector_count=collector_count+2
        else:
            collector_count=8
    elif(tmp[0][0:4]=='haGe'):
        collector[0,6]=float(tmp[0][4:])
        collector[0,7]=stand_time+float(tmp[1][:-1])
        data=np.append(data,collector,axis=0)
        collector=np.zeros((1,12))


speed=np.zeros(int(len(gps_buffer)/2))
for i in range(0,len(gps_buffer)):
    tmp=gps_buffer[i].split(',')
    if(len(tmp)==3):
        gps_collector[0,2]=float(tmp[1])
        gps_collector[0,3]=float(tmp[2])
        tmp=tmp[0].split(' ')
        tmp=tmp[1].split(':')
        time=(int(tmp[0])*3600+int(tmp[1])*60+int(tmp[2]))*1000
        gps_collector[0,4]=time
        gps=np.append(gps,gps_collector,axis=0)
    elif(len(tmp)==2):
        gps_collector[0,0]=float(tmp[1])
        speed[int(i/2)]=tmp[1]
        tmp=tmp[0].split(' ')
        tmp=tmp[1].split(':')
        time=(int(tmp[0])*3600+int(tmp[1])*60+int(tmp[2]))*1000
        gps_collector[0,1]=time
        

'''
#plot speed
plt.figure()
plt.plot(range(int(len(gps_buffer)/2)), speed[:])
plt.ylabel('speed')
plt.xlabel('time');
'''

#data_size=len(data)
tmp=data
collector=np.zeros((1,12))
data=np.zeros((1,12))
j=0
a=len(data)
for i in range(0,len(tmp)):
#while(data[j]):
    #if (len((np.where(data[j]==0))[0])!=0):
    if (len((np.where(tmp[i]==0))[0])!=0):
        #data=np.delete(data,j,0)
        stand_time=tmp[i,7]
    else:
        collector[0,:]=tmp[i,:]
        data=np.append(data,collector,axis=0)
        j=j+1;

data=np.delete(data,0,0)
'''
#base on gear time
final_data=np.zeros((len(data)-1,8))
state=-1
j=0
for i in range(0,len(data)-1):
    stand_time=data[i,7]
    while(stand_time>gps[j,1]):
        j=j+1
        if(j>=len(gps)):
            break
    if(j>=len(gps)):
            break
    
    final_data[i,0]=gps[j-1,2]+((gps[j,2]-gps[j-1,2])*(stand_time-gps[j-1,1])/(gps[j,1]-gps[j-1,1]))
    final_data[i,1]=gps[j-1,3]+((gps[j,3]-gps[j-1,3])*(stand_time-gps[j-1,1])/(gps[j,1]-gps[j-1,1]))
    final_data[i,4]=gps[j-1,0]+((gps[j,0]-gps[j-1,0])*(stand_time-gps[j-1,1])/(gps[j,1]-gps[j-1,1]))
    
    final_data[i,2]=data[i,4]+((data[i+1,4]-data[i,4])*((stand_time-data[i,5])/(data[i+1,5]-data[i,5])))
    final_data[i,3]=data[i,6]
    final_data[i,5]=max(data[i,8],data[i,10])+((max(data[i+1,8],data[i+1,10])-max(data[i,8],data[i,10]))*((stand_time-data[i,9+np.argmax(data[i,8:11:2],0)*2])/(data[i+1,9+np.argmax(data[i,8:11:2],0)*2]-data[i,9+np.argmax(data[i,8:11:2],0)*2])))
    final_data[i,6]=data[i,0]+((data[i+1,0]-data[i,0])*((stand_time-data[i,1])/(data[i+1,1]-data[i,1])))
    final_data[i,7]=data[i,2]+((data[i+1,2]-data[i,2])*((stand_time-data[i,3])/(data[i+1,3]-data[i,3])))
    

'''
#static time step
time_step=300
data_size=int((data[len(data)-1,7]-data[1,7])/time_step)
final_data=np.zeros((data_size,9))
#time_date=
state=-1
j=0
i=0
k=0
l=0
m=0
n=0

z=0
stand_time=data[1,7]
#for i in range(0,len(data)-1):
    
while(i<len(data) and j<len(gps)):
    while(stand_time+2000>=gps[j,1]):
        j=j+1
        if(j>=len(gps)):
            break
        
    if(j>=len(gps)):
            break
        
    while(stand_time>=data[i,5]):
        i=i+1
        if(i>=len(data)):
            break
        
    if(i>=len(data)):
            break
        
    while(stand_time>=data[k,7]):
        k=k+1
        if(k>=len(data)):
            break
        
    if(k>=len(data)):
            break
        
    while(stand_time>=data[l,9]):
        l=l+1
        if(l>=len(data)):
            break
        
    if(l>=len(data)):
            break
    
    while(stand_time>=data[m,1]):
        m=m+1
        if(m>=len(data)):
            break
        
    if(m>=len(data)):
            break
    
    while(stand_time>=data[n,3]):
        n=n+1
        if(n>=len(data)):
            break
        
    if(n>=len(data)):
            break
    
    while(data[k,7]>stand_time+3000):
        stand_time=stand_time+time_step
    
    
    final_data[z,5]=max(data[l-1,8],data[l-1,10])+((max(data[l,8],data[l,10])-max(data[l-1,8],data[l-1,10]))*((stand_time-data[l-1,9+np.argmax(data[l-1,8:11:2],0)*2])/(data[l,9+np.argmax(data[l-1,8:11:2],0)*2]-data[l-1,9+np.argmax(data[l-1,8:11:2],0)*2])))
    
    if(final_data[z,5]<0):
        stand_time=stand_time+time_step
        continue
    if(z==359):
        print(i)
    final_data[z,0]=gps[j-1,2]+((gps[j,2]-gps[j-1,2])*(stand_time-gps[j-1,1])/(gps[j,1]-gps[j-1,1]))
    final_data[z,1]=gps[j-1,3]+((gps[j,3]-gps[j-1,3])*(stand_time-gps[j-1,1])/(gps[j,1]-gps[j-1,1]))
    final_data[z,4]=gps[j-1,0]+((gps[j,0]-gps[j-1,0])*(stand_time-gps[j-1,1])/(gps[j,1]-gps[j-1,1]))
    
    final_data[z,2]=data[i-1,4]+((data[i,4]-data[i-1,4])*((stand_time-data[i-1,5])/(data[i,5]-data[i-1,5])))
    final_data[z,3]=data[k,6]
    
    final_data[z,6]=data[m-1,0]+((data[m,0]-data[m-1,0])*((stand_time-data[m-1,1])/(data[m,1]-data[m-1,1])))
    final_data[z,7]=data[n-1,2]+((data[n,2]-data[n-1,2])*((stand_time-data[n-1,3])/(data[n,3]-data[n-1,3])))
    
    final_data[z,8]=stand_time
    z=z+1
    stand_time=stand_time+time_step
    #print(stand_time)
    
d.close()
f.close()
np.savetxt('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_pv2_3_timesave.csv',final_data, delimiter=',',header="lati,long,Gyro,Gear,Rate,Pressure,Heartbeat,Temp,Time",comments='')
#np.savetxt('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_pv2_3_timesave.csv',final_data, delimiter=',')

df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_pv2_3_timesave.csv')
time=df['Time'].to_numpy()
time=time/1000
hour=(time/3600)
hour = np.array(list(map(np.int, hour)))
time=time-hour*3600

minute=(time/60)
minute = np.array(list(map(np.int, minute)))
time=time-minute*60

sec=time
sec = np.array(list(map(np.int, sec)))

for i in range(len(time)):   
    df['Time'][i]=year+'-'+month+'-'+date+' '+str(hour[i])+':'+str(minute[i])+':'+str(sec[i])
    
df.to_csv('data/can_Internal_difference/static_IMU/multiprocess/0421/after_pv2_4_timesave.csv', index = False,header=False)

'''
(row,col)=df.shape
time_int=np.zeros(row)
for i in range(0,row):
    time=df['pickup_datetime'][i]
    a=time.split(" ")
    a=a[1].split(":")
    time_int[i]=int(a[0])*3600+int(a[1])*60+int(a[2])
    #df['Pressure'][i]=float(df['Pressure'][i].strip())
    
    #print(df['Pressure'][57])

for i in range(0,row-1):
    stand_time=df['gearTime'][i]
    print(stand_time)
    df['lati'][i]=df['lati'][i]+((df['lati'][i+1]-df['lati'][i])*(stand_time-time_int[i])/(time_int[i+1]-time_int[i]))
    df['long'][i]=df['long'][i]+((df['long'][i+1]-df['long'][i])*(stand_time-time_int[i])/(time_int[i+1]-time_int[i]))
    df['Gyro'][i]=df['Gyro'][i]+((df['Gyro'][i+1]-df['Gyro'][i])*(stand_time-df['GyroTime'][i])/(df['GyroTime'][i+1]-df['GyroTime'][i]))
    df['Rate'][i]=df['Rate'][i]+((df['Rate'][i+1]-df['Rate'][i])*(stand_time-df['RateTime'][i])/(df['RateTime'][i+1]-df['RateTime'][i]))
    df['Pressure'][i]=df['Pressure'][i]+((df['Pressure'][i+1]-df['Pressure'][i])*(stand_time-df['PressureTime'][i])/(df['PressureTime'][i+1]-df['PressureTime'][i]))
    df['Heartbeat'][i]=df['Heartbeat'][i]+((df['Heartbeat'][i+1]-df['Heartbeat'][i])*(stand_time-df['HeartTime'][i])/(df['HeartTime'][i+1]-df['HeartTime'][i]))
    df['Temp'][i]=df['Temp'][i]+((df['Temp'][i+1]-df['Temp'][i])*(stand_time-df['TempTime'][i])/(df['TempTime'][i+1]-df['TempTime'][i]))
df = df[df['Heartbeat'].notna()]
df.to_csv(r'data/can_Internal_difference/static_IMU/after_ID/0331/2021331112751output.csv', index = False)
'''
#for i in range(0,row):
    
    