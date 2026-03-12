#-*- coding: utf-8 -*-
import threading
import smbus
import time
import os
import socket
import pymysql
import csv
import numpy as np
import pandas as pd
import seaborn as sb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.tree import export_graphviz
from graphviz import Source
import visualize as vs
import re

#import csv
#-------------for gps--------
import serial
import threading as thd
DEVICE_ID='/dev/ttyACM0'
ser=serial.Serial(
    port=DEVICE_ID,
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
#----------------------------

#Connect to Server
target_host = "140.123.106.112"
#target_host = "140.123.106.112"
target_port = 6666
#target_port = 3306
#MySQL
MYSQL_DB = 'intellibike'
MYSQL_USER = 'ccuintellibike'
MYSQL_PASS = 'rvl122vision'
Data_Base = 'SELECT * FROM route'

bus = smbus.SMBus(1)
address = 0x04
cmd = 0x01
InterNet_state = ''
receive_string = ""
sensordata = ""
check_event = ""
upload_data = ""
past_data = ""
past_gear = 1
RF_sensor_data = [['','','','','']] #Arduino sensor data for Randomforest

lock = threading.Lock()

def check_internet():
    global InterNet_state
    returnal = os.system("ping -c 1 8.8.8.8")
    if returnal:
        print('ping fail')
        InterNet_state = "2"
        #print(InterNet_state)
    else:
        print('ping ok')
        InterNet_state = "1"
        #print(InterNet_state)
def ConvertStringToBytes(src):
    converted = []
    for b in src:
        converted.append(ord(b))
    return converted

def upLoad2Server(sent_data,client):
    print(target_host,':',target_port)
    # create socket
    # AF_INET 代表使用標準 IPv4 位址或主機名稱
    # SOCK_STREAM 代表這會是一個 TCP client
    # client 建立連線
    # 傳送資料給 target
    str_data = sent_data +'\0'#input("Client:")+'\0'
    try:
        print(str_data)
        client.send(str_data.encode())
        #time.sleep(1)
    #except: #如果傳送失敗等待重新連線後傳送
    except Exception as ex:
        print("[Online-Exception_000:]: {}".format(ex.args))
        client.connect((target_host, target_port))
        client.send(str_data.encode())
        #time.sleep(1)
#MySQL
def connect_mysql():  #連線資料庫
    global connect, cursor
    connect = pymysql.connect(host = target_host, db = MYSQL_DB, user = MYSQL_USER, password = MYSQL_PASS,
            charset = 'utf8', use_unicode = True)
    cursor = connect.cursor()
    

def output_SQL_data():
    #find_time = '2019-05-15 23:25:32'
    find_time = 'all'
    connect_mysql()
    try:
        lock.acquire()
        cursor.execute(Data_Base)
        lock.release()
        online_sql_data = cursor.fetchall()
    except Exception as ex:
        print("[Online-Exception_execute:]: {}".format(ex.args))
    with open('sql_output.csv','w',newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time','Lat','Lng','Gyro','Gear','Speed','Pressure','Heartbeat','Gear1'])
        csvfile.close()
    i = 0
    for row in online_sql_data:
        i += 1
        if str(row[0]) == find_time or find_time == 'all':
            find_time = 'all'
            with open('sql_output.csv','a',newline = '') as csvfile:
                Time = str(row[0])
                Lat = filter(lambda ch: ch in '0123456789.', str(row[1]))
                Lat = ''.join(list(Lat))
                Lng = filter(lambda ch: ch in '0123456789.', str(row[2]))
                Lng = ''.join(list(Lng))
                Gyro = filter(lambda ch: ch in '0123456789.', str(row[3]))
                Gyro = ''.join(list(Gyro))
                Gear = filter(lambda ch: ch in '0123456789.', str(row[4]))
                Gear = ''.join(list(Gear))
                Speed = filter(lambda ch: ch in '0123456789.', str(row[5]))
                Speed = ''.join(list(Speed))
                Pressure = filter(lambda ch: ch in '0123456789.', str(row[6]))
                Pressure = ''.join(list(Pressure))
                Heartbeat = filter(lambda ch: ch in '0123456789.', str(row[7]))
                Heartbeat = ''.join(list(Heartbeat))
                
                if i == 1:
                    Gear1 = ''
                else:
                    Gear1 = filter(lambda ch: ch in '0123456789.', str(online_sql_data[i - 2][4]))
                    Gear1 = ''.join(list(Gear1))

                #data = [str(row[0]),float(row[1]),float(row[2]),float(row[3]),float(row[4]),float(row[5]),float(row[6]),float(row[7])]
                #data = [str(row[0]),str(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5]),str(row[6]),str(row[7])]
                if Time == '' or Lat == '' or Lng == '' or Gyro == '' or Gear == '' or Speed == '' or Pressure == '' or Heartbeat == ''or Gear1 == '':
                    continue
                else:
                    writer = csv.writer(csvfile)
                    data = [Time, float(Lat), float(Lng), float(Gyro), float(Gear), float(Speed), float(Pressure), float(Heartbeat), float(Gear1)]
                    writer.writerow(data)
    ##            print('Time: ',row[0])
    ##            print('Lat: ',row[1])
    ##            print('Lng: ',row[2])
    ##            print('Gyro: ',row[3])
    ##            print('Gear: ',row[4])
    ##            print('Rate: ',row[5])
    ##            print('Pressure: ',row[6])
    ##            print('Heartbeat: ',row[7])
    ##            print('--------------------------------------------------------------------')
        csvfile.close()
        #cursor.close()

#Randomforest
def RF_process(sensor_data_arr):
    time_start = time.time()
    Intellibike_data_clean = pd.read_csv('sql_output.csv')
    all_inputs = Intellibike_data_clean[['Gyro', 'Speed',
                                         'Pressure','Heartbeat','Gear1']].values
    all_labels = Intellibike_data_clean['Gear'].values
    
    training_inputs = all_inputs[0:]
    #training_inputs = np.append(training_inputs, all_inputs[19:21], axis=0)
    #training_inputs = np.append(training_inputs, all_inputs[22:23], axis=0)

    testing_inputs = sensor_data_arr
    print('testing inputs: ',testing_inputs)
##    testing_inputs = np.append(testing_inputs, all_inputs[21:22], axis=0)
##    testing_inputs = np.append(testing_inputs, all_inputs[23:24], axis=0)

    training_classes = all_labels[0:]
    #training_classes = np.append(training_classes, all_labels[19:21], axis=0)
    #training_classes = np.append(training_classes, all_labels[22:23], axis=0)

##    testing_classes = all_labels[14:19]
##    testing_classes = np.append(testing_classes, all_labels[21:22], axis=0)
##    testing_classes = np.append(testing_classes, all_labels[23:24], axis=0)

    i = 150
    #while i < 110 :
        #i += 10
    forest = RandomForestClassifier(n_estimators = i) #最大迭代次數(可以10為單位調整)
    forest_fit = forest.fit(training_inputs, training_classes)

    test_y_predicted = forest.predict(testing_inputs)
        #print(testing_classes)
        #print(test_y_predicted)
        #accuracy = metrics.accuracy_score(testing_classes, test_y_predicted)
        #print('n_estimators = ' , i , 'Accuracy = ', accuracy)
        #if accuracy >=0.7 and i >= 200:
        #if i > 90:
##    '''
##    繪製樹狀圖(PC)
##    '''
##    for x in range(len(forest.estimators_)):
##        export_graphviz(forest.estimators_[x] , './results/%d.dot'%i)
##        file_name = str(x + 1)  
##    os.system('dot -Tpng ' + './results/' + str(file_name) + '.dot' + ' -o ' + './results/' + str(file_name) + '.png')
        
            #print(testing_classes)
            #print('predict = ',test_y_predicted)
    global Predicted_Gear
    Predicted_Gear = int(test_y_predicted[0])
            
    time_end = time.time()
    print('Random Forest Cost Time = ', time_end-time_start,'s')
            #vs.plot_prediction(testing_classes,test_y_predicted)
            #break
##        elif i == 400:
##            for x in range(len(forest.estimators_)):
##                export_graphviz(forest.estimators_[x] , './results/%d.dot'%i)
##                file_name = str(x + 1)
##            os.system('dot -Tpng ' + './results/' + str(file_name) + '.dot' + ' -o ' + './results/' + str(file_name) + '.png')
##        
##            #print(testing_classes)
##            print(test_y_predicted)
##            #vs.plot_prediction(testing_classes,test_y_predicted)
##            break
def test2222():
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
if __name__=='__main__':
    '''
    Check_InterNet_State
    '''
    # SOCK_STREAM 代表這會是一個 TCP client
    # client 建立連線
    day_time="0000"
    year="2021"
    month="00"
    date="00"
    hour="00"
    minu="00"
    sec="00"
    offline_flag=1
    connect_flag=1
    gear_flag=0
    sensor=['']
    sensor_clock=['']
    while(1):
        while(receive_string!="ok"):
            receive_string=""
            print("zzzzzz\n")
        #while(abc != 1):
            #r = input('Enter something, "q" to quit"')
            #print(r)
            check_internet()
            #print(InterNet_state)
            try:
                #check_internet()
                bytesToSend = ConvertStringToBytes(InterNet_state)
                #bytesToSend = ConvertStringToBytes("2")
                bus.write_i2c_block_data(address, cmd, bytesToSend)
                rep = bus.read_i2c_block_data(address,0)
                for i in range(0,32):   #32 = arduino端wire.write之buffer大小
                    if rep[i] != 255:
                        receive_string += chr(rep[i])
                    else:
                        #receive_string=""
                        continue
                print(receive_string)
                #check = 1
            except Exception as ex:
                print("[Exception:]: {}".format(ex.args))
        
        time.sleep(3)               ##釋放i2c內之buffer
        receive_string=""
#-----------------------------------------------------------------------
        '''
        Receive Arduino Data
        '''
        #---------------------------------connect to PC--------------------------------------

        
        if (InterNet_state == '1'):#連線狀態 
            '''
            #past_gear = 0
            if (connect_flag==1):
                #連接至Server
                connect_flag=0
                try:
                    print("aaa\n")
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("bbb\n")
                    client.connect((target_host, target_port))
                    print("ccc\n")
                except Exception as ex:
                    print("[Online-connect-Exception_1:]: {}".format(ex.args))
            '''
        #---------------------------------connect to PC end--------------------------------------
#-------------------------loop-for-upload-offline-data----start------------------------------
        
            '''
            if (offline_flag==1):
                offline_flag=0
                while(1):
                    try:
                        rep = bus.read_i2c_block_data(address,0)
                        for i in range(0,32):   #32 = arduino端wire.write之buffer大小
                            print(i)
                            if rep[i] != 255:
                                sensordata += chr(rep[i])
                            else:
                                continue
                        print("\n")
                        print("offline_data")
                        print(sensordata)
                        print("\n")
                        print("111\n")
                        if sensordata=="OfflineUpload":
                            print("222\n")
                            rep=""
                            upload_data = ""
                            sensordata = ""
                            bytesToSend = ""
                            past_data = ""
                            time.sleep(1)
                            break;
                        print("333\n")
                        bytesToSend = ConvertStringToBytes("1")#1110test
                        bus.write_i2c_block_data(address, cmd, bytesToSend)#1110test
                        if sensordata[2:4] != past_data:
                                print("444\n")
                                past_data = sensordata[2:4]
                                upload_data = sensordata[2:]
                                upLoad2Server(upload_data,client)
                                

                    except Exception as ex:
                        print("[NetCheck-Exception:]: {}".format(ex.args))
                    
                    rep=""
                    upload_data = ""
                    sensordata = ""
                    bytesToSend = ""
                    
                    time.sleep(1)
                    
                time.sleep(1)
                bytesToSend = ConvertStringToBytes("1")#1110test
                bus.write_i2c_block_data(address, cmd, bytesToSend)#1110test
                '''
        
#-------------------------loop-for-upload-offline-data------end------------------------------
            
            # 建立子執行緒
            sql_data = threading.Thread(target = output_SQL_data)
            #test123 = threading.Thread(target = test2222)
            # 開始下載sql data
            sql_data.start()
            #sql_data.join()
            #test123.start()
            #test123.join()
            
            check_event = ""
            #while(check_event!="ha"):
            year=str(time.localtime().tm_year);
            month=str(time.localtime().tm_mon);
            date=str(time.localtime().tm_mday);
            hour=str(time.localtime().tm_hour);
            minu=str(time.localtime().tm_min);
            sec=str(time.localtime().tm_sec);
            
            with open('output/'+year+month+date+hour+minu+sec+'output.csv','w') as csvfile:
            #with open('output.csv','w') as csvfile:
                writer=csv.writer(csvfile)
                while(1):
                    time.sleep(0.3)
                    time_data=""
                    try:
                        print("aaa")
                        rec = bus.read_i2c_block_data(address,0)
                        
                    #except Exception as ex:
                    #    print("[Online-read-Exception_2:]: {}".format(ex.args))
                    #try:
                        #check = 1
                        for i in range(0,32):   #32 = arduino端wire.write之buffer大小
                            #print(i)
                            if rec[i] != 255:
                                sensordata += chr(rec[i])
                            else:
                                continue
                        print(sensordata)
                        split_sensor=sensordata.split(',')
                        bytesToSend = ConvertStringToBytes("1")#1110test
                        bus.write_i2c_block_data(address, cmd, bytesToSend)#1110test
                        
                        for i in range(0,len(split_sensor)):
                            sensordata=split_sensor[i]
                        
                            print(split_sensor)
                            
                            check_event = sensordata[0:2]
                            
                            if sensordata[2:4] != past_data:
                                past_data = sensordata[2:4]
                                upload_data = sensordata[2:]
                                #過濾非數字字元後做Randomforest Inputs                        
                                if past_data[0] == 'G' and past_data[1] == 'y':
                                    split_data=upload_data.split(';')
                                    sensor.append(split_data[0][2:])
                                    #sensor_clock.append(split_data[1])
                                    if(int(sensor_clock[1])<=int(split_data[1])):
                                        #sensor_clock.append(str(int(int(split_data[1])/10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])-int(sensor_clock[1]))/10+clock)))
                                    else:
                                        #sensor_clock.append(str(int(int(split_data[1])/10+10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])+100-int(sensor_clock[1]))/10+clock)))
                                    
                                    #sensor.append(upload_data[2:])
                                    time_data="Gy"
                                    
                                elif past_data[0] == 'R':
                                    split_data=upload_data.split(';')
                                    sensor.append(split_data[0][1:])
                                    
                                    #sensor.append(upload_data[1:])
                                    time_data="R"
                                    
                                    hour1=str(time.localtime().tm_hour);
                                    minu1=str(time.localtime().tm_min);
                                    sec1=str(time.localtime().tm_sec);
                                    clock=(time.localtime().tm_hour*60+time.localtime().tm_min)*60+time.localtime().tm_sec
                                    #sensor_clock.append(str(int(int(split_data[1])/10+clock)))
                                    
                                    sensor_clock.append(str(int(split_data[1])))
                                    #sensor_clock.append(str(int(clock)))
                                    
                                    #time_data=time_data+" "+hour+":"+minu+":"+sec
                                    #sensor.append(time_data)
                                    
                                elif past_data[0] == 'P':
                                    split_data=upload_data.split(';')
                                    sensor.append(split_data[0][1:])
                                    
                                    if(int(sensor_clock[1])<=int(split_data[1])):
                                        #sensor_clock.append(str(int(int(split_data[1])/10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])-int(sensor_clock[1]))/10+clock)))
                                    else:
                                        #sensor_clock.append(str(int(int(split_data[1])/10+10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])+100-int(sensor_clock[1]))/10+clock)))
                                    
                                    
                                    #sensor.append(upload_data[1:])
                                    time_data="P"
                                    
                                elif past_data[0] == 'H':
                                    split_data=upload_data.split(';')
                                    sensor.append(split_data[0][1:])
                                    #sensor_clock.append(split_data[1])
                                    
                                    if(int(sensor_clock[1])<=int(split_data[1])):
                                        #sensor_clock.append(str(int(int(split_data[1])/10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])-int(sensor_clock[1]))/10+clock)))
                                    else:
                                        #sensor_clock.append(str(int(int(split_data[1])/10+10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])+100-int(sensor_clock[1]))/10+clock)))
                                    #sensor.append(upload_data[1:])
                                    time_data="H"
                                    
                                elif past_data[0] == 'G' and past_data[1] == 'e':
                                    split_data=upload_data.split(';')
                                    sensor.append(split_data[0][2:])
                                    #sensor_clock.append(split_data[1])
                                    
                                    if(int(sensor_clock[1])<=int(split_data[1])):
                                        #sensor_clock.append(str(int(int(split_data[1])/10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])-int(sensor_clock[1]))/10+clock)))
                                    else:
                                        #sensor_clock.append(str(int(int(split_data[1])/10+10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])+100-int(sensor_clock[1]))/10+clock)))
                                    #sensor.append(upload_data[2:])
                                    past_gear = float(split_data[0][2:])
                                    gear_flag=1
                                    time_data="Ge"
                                    '''
                                    upLoad2Server(upload_data,client)
                                    print("ccc")
                                    print(upload_data)
                                    break;
                                    '''
                                elif past_data[0] == 'T' and past_data[1] != 'e' and gear_flag==1:
                                    #upLoad2Server(upload_data,client)
                                    print("bbb1\n")
                                    '''
                                    while(True):
                                        print("bbb2\n")
                                        All_GPS_Data=str(ser.readline())
                                        print(All_GPS_Data)
                                        Splitted_GPS_Data=All_GPS_Data.split(',')
                                        if Splitted_GPS_Data[0]=="b'$GNZDA":
                                            print("bbb3\n")
                                            if Splitted_GPS_Data[2]=="":
                                                a=0
                                                print("bbb\n")
                                            else:
                                                year=Splitted_GPS_Data[4]
                                                month=Splitted_GPS_Data[3]
                                                date=Splitted_GPS_Data[2]
                                                break
                                    '''
                                    year=str(time.localtime().tm_year);
                                    month=str(time.localtime().tm_mon);
                                    date=str(time.localtime().tm_mday);
                                    hour=str(time.localtime().tm_hour);
                                    minu=str(time.localtime().tm_min);
                                    sec=str(time.localtime().tm_sec);
                                    
                                    #upload_data="T"+year+"-"+month+"-"+date+" "+hour+":"+minu+":"+sec
                                    time_data="T"+year+"-"+month+"-"+date+" "+hour+":"+minu+":"+sec
                                    gear_flag=0
                                    upLoad2Server(time_data,client)
                                    time.sleep(1)
                                    print(time_data)
                                    #break
                                #bytesToSend = ConvertStringToBytes("1")#1110
                                #bus.write_i2c_block_data(address, cmd, bytesToSend)#1110
                                                            
                                #elif past_data[0] == 'L'and past_data[1] == 'n':
                                #    time_data="Gp"
                                #    upload_data="Lng"+str(lang)[0:7]
                                #    print("aaa11\n")
                                elif past_data[0] == 'T' and past_data[1] == 'e':
                                    split_data=upload_data.split(';')
                                    sensor.append(split_data[0][2:])
                                    #sensor_clock.append(split_data[1])
                                    
                                    if(int(sensor_clock[1])<=int(split_data[1])):
                                        #sensor_clock.append(str(int(int(split_data[1])/10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])-int(sensor_clock[1]))/10+clock)))
                                    else:
                                        #sensor_clock.append(str(int(int(split_data[1])/10+10+clock)))
                                        sensor_clock.append(str(int((int(split_data[1])+100-int(sensor_clock[1]))/10+clock)))
                                    #sensor.append(upload_data[2:])
                                    time_data="Te"
                                elif past_data[0] == 'L'and past_data[1] == 'a':
                                    print("aaa1\n")
                                    time_data="Gp"
                                    while(True):
                                        print("aaa2\n")
                                        All_GPS_Data=str(ser.readline())
                                        print(All_GPS_Data)
                                        Splitted_GPS_Data=All_GPS_Data.split(',')
                                        if Splitted_GPS_Data[0]=="b'$GNGGA":
                                            print("aaa3\n")
                                            if Splitted_GPS_Data[2]=="":
                                                a=0
                                                print("aaa\n")
                                            else:
                                                '''
                                                #get time information--------------------
                                                day_time=Splitted_GPS_Data[1]
                                                print("day_time:")
                                                print(day_time)
                                                hour=str(int(day_time[0:2])+8)
                                                minu=day_time[2:4]
                                                sec=day_time[4:6]
                                                #----------------------------------------
                                                '''
                                                print("aaa4\n")
                                                lati=0
                                                lang=0
                                                print(Splitted_GPS_Data[2]+","+Splitted_GPS_Data[3]," "+
                                                      Splitted_GPS_Data[4]+","+Splitted_GPS_Data[5])
                                                degree_lati=int(Splitted_GPS_Data[2][0:2])
                                                minute_lati=float(Splitted_GPS_Data[2][2:])/60
                                                print("aaa5\n")
                                                '''LATI, THE DEGREE DATA OF GPS'''
                                                lati=degree_lati+minute_lati
                                                print("aaa6\n")
                                                if Splitted_GPS_Data[3]=='S':
                                                    lati=0-lati
                                                print("aaa7\n")
                                                degree_lang=int(Splitted_GPS_Data[4][0:3])
                                                minute_lang=float(Splitted_GPS_Data[4][3:])/60
                                                print("aaa8\n")
                                                '''LANG, THE DEGREE DATA OF GPS'''
                                                lang=degree_lang+minute_lang
                                                if Splitted_GPS_Data[5]=='W':
                                                    lang=0-lang
                                                print("aaa9\n")
                                                
                                                sensor.append(str(lati)[0:7])
                                                sensor.append(str(lang)[0:8])
                                                
                                                year=str(time.localtime().tm_year);
                                                month=str(time.localtime().tm_mon);
                                                date=str(time.localtime().tm_mday);
                                                hour=str(time.localtime().tm_hour);
                                                minu=str(time.localtime().tm_min);
                                                sec=str(time.localtime().tm_sec);
                                                
                                                #upload_data="T"+year+"-"+month+"-"+date+" "+hour+":"+minu+":"+sec
                                                time_data=year+"-"+month+"-"+date+" "+hour+":"+minu+":"+sec
                                                sensor.append(time_data)
                                                gear_flag=0
                                                sensor_clock[1]=(str(int(clock)))
                                                print(sensor)
                                                print(sensor_clock)
                                                
                                                
                                                writer.writerow([sensor[9],sensor[7],sensor[8],sensor[3],sensor[6],sensor[1],sensor[2],sensor[4],sensor[5],sensor_clock[6],sensor_clock[4],sensor_clock[3],sensor_clock[1],sensor_clock[2],sensor_clock[5]])
                                                print(time_data)
                                                '''
                                                upLoad2Server(upload_data,client)
                                                #print("ccc")
                                                print(upload_data)
                                                year=str(time.localtime().tm_year)
                                                month=str(time.localtime().tm_mon)
                                                date=str(time.localtime().tm_mday)
                                                hour=str(time.localtime().tm_hour)
                                                minu=str(time.localtime().tm_min)
                                                sec=str(time.localtime().tm_sec)
                                                time.sleep(1)
                                                time_data=time_data+"T"+year+"-"+month+"-"+date+" "+hour+":"+minu+":"+sec
                                                upLoad2Server(time_data,client)
                                                print(time_data)
                                                '''
                                                sensor=['']
                                                sensor_clock=['']
                                                break
                                
                                #time.sleep(0.3)
                                '''
                                if time_data != "":
                                    year=str(time.localtime().tm_year)
                                    month=str(time.localtime().tm_mon)
                                    date=str(time.localtime().tm_mday)
                                    hour=str(time.localtime().tm_hour)
                                    minu=str(time.localtime().tm_min)
                                    sec=str(time.localtime().tm_sec)
                                        
                                    time_data=time_data+"T"+year+"-"+month+"-"+date+" "+hour+":"+minu+":"+sec
                                    upLoad2Server(time_data,client)
                                    print(time_data)
                                '''
                                print(sensor)
                                print(sensor_clock)

                                if RF_sensor_data[0][0] != '' and RF_sensor_data[0][1] != '' and RF_sensor_data[0][2] != '' and RF_sensor_data[0][3] != '':
                                    '''
                                    if past_gear == 0:
                                        past_gear = 1
                                    '''
                                    #print(float(past_gear))
                                    print('past_gear = ',past_gear)
                                
                            
                    except Exception as ex:
                        print("[Online-Exception_2:]: {}".format(ex.args))
                    
                    rec = ""
                    upload_data = ""
                    sensordata = ""
                    bytesToSend = ""
                    #print("SQL_Data")
                    #connect_mysql()
                    #output_SQL_data()
                    #time.sleep(1)
        elif (InterNet_state == '2'):#離線狀態
            offline_flag=1
            #past_gear = 0
        #while(1):
            check_event = ""
            #while(check_event!="ha"):
            while(1):
                try:
                    rec = bus.read_i2c_block_data(address,0)
                    #check = 1
                    for i in range(0,32):   #32 = arduino端wire.write之buffer大小
                        if rec[i] != 255:
                            sensordata += chr(rec[i])
                        else:
                            continue
                    check_event = sensordata[0:2]
                    if sensordata[2:4] != past_data:
                        past_data = sensordata[2:4]
                        upload_data = sensordata[2:]
                        #過濾非數字字元後做Randomforest Inputs
                        if past_data[0] == 'G' and past_data[1] == 'y':
                            #RF_sensor_data[0][0] = float(upload_data[2:])
                            RF_sensor_data[0][0] = filter(lambda ch: ch in '0123456789.', str(upload_data[2:]))
                            RF_sensor_data[0][0] = ''.join(list(RF_sensor_data[0][0]))
                            RF_sensor_data[0][0] = float(RF_sensor_data[0][0])
                            
                        if past_data[0] == 'R':
                            #RF_sensor_data[0][1] = float(upload_data[1:])
                            RF_sensor_data[0][1] = filter(lambda ch: ch in '0123456789.', str(upload_data[1:]))
                            RF_sensor_data[0][1] = ''.join(list(RF_sensor_data[0][1]))
                            RF_sensor_data[0][1] = float(RF_sensor_data[0][1])
                            
                        if past_data[0] == 'P':
                            #RF_sensor_data[0][2] = float(upload_data[1:])
                            RF_sensor_data[0][2] = filter(lambda ch: ch in '0123456789.', str(upload_data[1:]))
                            RF_sensor_data[0][2] = ''.join(list(RF_sensor_data[0][2]))
                            RF_sensor_data[0][2] = float(RF_sensor_data[0][2])
                            
                        if past_data[0] == 'H':
                            #RF_sensor_data[0][3] = float(upload_data[1:])
                            RF_sensor_data[0][3] = filter(lambda ch: ch in '0123456789.', str(upload_data[1:]))
                            RF_sensor_data[0][3] = ''.join(list(RF_sensor_data[0][3]))
                            RF_sensor_data[0][3] = float(RF_sensor_data[0][3])
                        if past_data[0] == 'G' and past_data[1] == 'e':
                            past_gear = float(upload_data[2:])
                            gear_flag=1
                            '''
                            upLoad2Server(upload_data,client)
                            print("ccc")
                            print(upload_data)
                            break;
                            '''
                        if past_data[0] == 'T' and past_data[1] != 'e' and gear_flag==1:
                            gear_flag=0
                            upLoad2Server(upload_data,client)
                            print(upload_data)
                            break
                        bytesToSend = ConvertStringToBytes("1")
                        bus.write_i2c_block_data(address, cmd, bytesToSend)
                        
                        #upLoad2Server(upload_data,client)
                        print(upload_data)
                        #print(RF_sensor_data)
                        
                        if RF_sensor_data[0][0] != '' and RF_sensor_data[0][1] != '' and RF_sensor_data[0][2] != '' and RF_sensor_data[0][3] != '':
                            '''
                            if past_gear == 0:
                                past_gear = 1
                            '''
                            print('past_gear = ',past_gear)
                            time.sleep(1)
                            #break;
                except Exception as ex:
                    print("[Offline-Exception:]: {}".format(ex.args))
                upload_data = ""
                sensordata = ""
                rec = ""
                bytesToSend = ""
                #print("SQL_Data")
                #connect_mysql()
                #output_SQL_data()
                time.sleep(1)




