# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import joblib
import lightgbm as lgb

from deepforest import CascadeForestClassifier

#df = pd.read_csv('route.csv')
#df = pd.read_csv('202139155048output.csv')
#df = pd.read_csv('data/2021317121841output.csv')
#df = pd.read_csv('data/2021318114351output.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/after_ID/all_data.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/after_ID/after_GS.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/all_data.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0421/after_GS_4.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/after_GS_skip_freetime_0504.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/after_OSM_0515.csv')
df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/outside_0610.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/add_outside_0604.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/add_0515_0610.csv')


#df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0519_out/after_GS_skip_freetime.csv')
#df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/out_test_0521.csv')
#df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/test_0521_2000.csv')
df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/outside_test_0604.csv')

cat_cols = ['Hour', 'AMorPM', 'Weekday']
cont_cols = ['lati', 'long','Gyro', 'Rate', 'Pressure', 'Heartbeat','Temp','map_inf']
#cont_cols = ['lati', 'long','Gyro', 'Rate', 'Pressure', 'Heartbeat','Temp']
#cont_cols = ['lati', 'long', 'Rate', 'Heartbeat', 'Pressure','Temp']
#cont_cols = ['lati', 'long', 'Rate', 'Pressure', 'Heartbeat','Temp','map_inf']
#cont_cols = ['Rate', 'Pressure']

y_col = ['Gear']  # this column contains the labels

conts_t = np.stack([df_t[col].values for col in cont_cols], 1)
conts = np.stack([df[col].values for col in cont_cols], 1)

y_t = np.stack([df_t[col].values for col in y_col], 1)
y = np.stack([df[col].values for col in y_col], 1)

'''
lat_mean=conts[:,0].mean(0)
long_mean=conts[:,1].mean(0)
for i in range(df.index.stop):
    if (abs(conts[i][0]-lat_mean)>0.01):
        conts[i][0]=conts[i-1][0]
    if (abs(conts[i][1]-long_mean)>0.02):
        conts[i][1]=conts[i-1][1]


lat_mean=conts_t[:,0].mean(0)
long_mean=conts_t[:,1].mean(0)
for i in range(df_t.index.stop):
    if (abs(conts_t[i][0]-lat_mean)>0.01):
        conts_t[i][0]=conts_t[i-1][0]
    if (abs(conts_t[i][1]-long_mean)>0.02):
        conts_t[i][1]=conts_t[i-1][1]
'''

'''
plt.figure()
#plt.plot(range(test_size), df['Gear'][-test_size:])
plt.plot(range(df_t.index.stop), conts_t[:df_t.index.stop,1])
plt.ylabel('gear')
plt.xlabel('time');

plt.figure()
#plt.plot(range(test_size), df['Gear'][-test_size:])
plt.plot(range(df_t.index.stop), conts_t[:df_t.index.stop,0])
plt.ylabel('gear')
plt.xlabel('time');
'''


#--past gps----
conts_t = np.c_[ conts_t, np.zeros(df_t.index.stop)]
conts_t = np.c_[ conts_t, np.zeros(df_t.index.stop)]
conts=np.c_[ conts, np.zeros(df.index.stop)]
conts=np.c_[ conts, np.zeros(df.index.stop)]


conts_t[0,-2:]=conts_t[0,:2]
conts[0,-2:]=conts[0,:2]

conts_t[1:,-2:]=conts_t[:-1,:2]
conts[1:,-2:]=conts[:-1,:2]
cont_cols=cont_cols+['past_lati','past_long']
#--past gps end----




cont_cols_buf=cont_cols
conts_t_buf=conts_t
conts_buf=conts
#for i in range(3):
#for i in range(69):
for i in range(3):
    i
    cont_cols=cont_cols+cont_cols_buf
    conts_t=np.concatenate((conts_t, conts_t_buf), axis=1)
    conts=np.concatenate((conts,conts_buf), axis=1)
    
#conts_t=np.c_[ conts_t, np.r_[0,df_t['Gear'][0:df_t.index.stop-1].values]]
conts_t = np.c_[ conts_t, np.zeros(df_t.index.stop)+1]
#conts_t = np.c_[ conts_t, np.zeros(df_t.index.stop)+2]
conts=np.c_[ conts, np.r_[0,df['Gear'][0:df.index.stop-1].values]]

cont_cols=cont_cols+['past_gear']


'''
conts_t = np.c_[ conts_t, np.zeros(df_t.index.stop)+2]
conts=np.c_[ conts, np.zeros(df.index.stop)+2]
'''



'''
conts_t[:,:]=(conts_t[:,:]-conts[:,:].mean(0))/conts[:,:].std(0) # feature scaling
conts[:,:]=(conts[:,:]-conts[:,:].mean(0))/conts[:,:].std(0) # feature scaling
'''
conts_t[:,:-1]=(conts_t[:,:-1]-conts[:,:-1].mean(0))/conts[:,:-1].std(0) # feature scaling
conts[:,:-1]=(conts[:,:-1]-conts[:,:-1].mean(0))/conts[:,:-1].std(0) # feature scaling



test_size = int(df_t.index.stop)
#test_size=2000;

#con_train = conts[:-test_size]
con_train = conts[:]
#con_test = conts[-test_size:]
con_test = conts_t[0:]

#y_train = y[:-test_size]
y_train = y[:]
#y_test = y[-test_size:]
y_test = y_t[0:]

tp=1
if(tp<1):
    con_train = np.r_[ con_train[0:int(10000*tp),:],con_train[14000:int(14000+10000*tp),:],con_train[24000:int(24000+10000*tp),:]\
                  ,con_train[34000:int(34000+10000*tp),:],con_train[44000:int(44000+10000*tp),:]]
        
    y_train = np.r_[ y_train[0:int(10000*tp),:],y_train[14000:int(14000+10000*tp),:],y_train[24000:int(24000+10000*tp),:]\
                      ,y_train[34000:int(34000+10000*tp),:],y_train[44000:int(44000+10000*tp),:]]


#Import Random Forest Model
#------RF-----------------------------------


#Create a Gaussian Classifier
clf=RandomForestClassifier(n_estimators=70,min_samples_leaf = 6)
#clf2=RandomForestClassifier(n_estimators=0,min_samples_leaf = 6,warm_start=1)

#clf=RandomForestClassifier(n_estimators=70,max_depth=11,min_samples_leaf = 6)
clf2=RandomForestClassifier(n_estimators=0,max_depth=11,min_samples_leaf = 6,warm_start=1)

#Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(con_train,y_train)

feature_imp = pd.Series(clf.feature_importances_,index=cont_cols).sort_values(ascending=False)
feature_imp
#y_val=clf.predict(con_test[0:test_size])

#two step
y_val=clf.predict(con_train[0:])

con_train[1:,-1]=y_val[0:-1]
#clf2.fit(con_train,y_train)
z=0
for i in range(80) :
    print(i)
    if(i==79):
        clf2.n_estimators += 80#增加樹
    else:
        #clf2.n_estimators += (int(i/10) +1)
        clf2.n_estimators += (1)
        #clf2.fit(con_train,y_train)
        #z=1
    #else:
    
    clf2.fit(con_train,y_train)
    
    con_train[1:,-1]=clf2.predict(con_train)[:-1]
    
joblib.dump(clf2, 'LR_model')


a=np.zeros((1,401))
a=np.zeros((1,41))

#a=np.zeros((1,9))
#a=np.zeros((1,11))


#a=np.zeros((1,37))
#a=np.zeros((1,11))
y_val=np.zeros(test_size)
for i in range(test_size):
    print(i)
    a[0,:]=con_test[i,:]
    #y_val[i] = clf.predict(a)
    y_val[i] = clf2.predict(a)
    print("y:",y_val[i])
    if(i<test_size-1):
        con_test[i+1,-1]=y_val[i]
        
#------RF END-----------------------------------
'''
#-----------Deep Forest------------------------
model = CascadeForestClassifier(n_estimators=1,random_state=1,n_jobs=8,n_tolerant_rounds =2,n_trees=70,max_depth=11,min_samples_leaf = 6)
model.fit(con_train, y_train)

#feature_imp = pd.Series(model.feature_importances_,index=cont_cols).sort_values(ascending=False)
#feature_imp
a=np.zeros((1,701))
#a=np.zeros((1,3))
#a=np.zeros((1,10))
y_val=np.zeros(test_size)
for i in range(test_size):
    print(i)
    a[0,:]=con_test[i,:]
    y_val[i] = model.predict(a)
    print("y:",y_val[i])
    if(i<test_size-1):
        con_test[i+1,-1]=y_val[i]
#y_val = model.predict(con_test[0:test_size])
#-----------Deep Forest END------------------------
'''

# Model Accuracy, how often is the classifier correct?
print("Accuracy:",metrics.accuracy_score(y_test[0:test_size], y_val))

plt.figure()
#plt.plot(range(test_size), df['Gear'][-test_size:])
plt.plot(range(test_size), df_t['Gear'][:test_size])
plt.ylabel('gear')
plt.xlabel('time');


test_count=0
test_count=np.zeros(6)
test_er=0
test_gear=np.zeros(test_size)

slide_size=5
change_feq=0
change_score=0

for i in range(test_size):
    #if(i%slide_size==0 and i+slide_size<test_size):
    if(i+slide_size<test_size):
        change_feq=0
        for j in range(slide_size):
            if(y_val[i+j]!=y_val[i+j+1]):
                change_feq=change_feq+1
                
    if(change_feq>=int(slide_size*0.5)):
        change_score=change_score-change_feq
        
    if(y_val[i]==y_test[i]):
        test_count[0]=test_count[0]+1
        #test_count=test_count+1
    elif(abs(y_val[i]-y_test[i])==1):
        test_count[1]=test_count[1]+1
    elif(abs(y_val[i]-y_test[i])==2):
        test_count[2]=test_count[2]+1
    elif(abs(y_val[i]-y_test[i])==3):
        test_count[3]=test_count[3]+1
    elif(abs(y_val[i]-y_test[i])==4):
        test_count[4]=test_count[4]+1
    elif(abs(y_val[i]-y_test[i])==5):
        test_count[5]=test_count[5]+1
    else:
        test_er=test_er+(np.array(y_val[i]).argmax()-np.array(y_test[i]).argmax())**2
    
    '''
    diff = np.abs(np.array(y_val[i])-np.array(y_test[i]))
    print(diff)
    #print(f'{i+1:2}. {y_val[i]:8.4f} {y_test[i]:8.4f} {diff:8.4f}')
    '''
print(test_count[:]/test_size)
print("scoure:",test_count[0]/test_size+change_score/test_size)

plt.plot(range(test_size), y_val[:])
plt.legend(['ground turth','predict'],loc = 1)
plt.ylabel('gear')
plt.xlabel('time');
plt.show()

plt.figure()
gap = ['0', '1', '2', '3','4','5']
x = np.arange(len(gap))
plt.bar(x, test_count[:]/test_size, color=['green'])
plt.xticks(x, gap)
plt.xlabel('gap level')
plt.ylabel('percentage')
plt.title('Gap percentage')
for x,y in enumerate(test_count[:]/test_size):plt.text(x,y,'%.3f'%y,ha='center')
plt.show()

#np.savetxt('DF.csv',y_val, delimiter=',')
np.savetxt('XGB_outside.csv',y_val, delimiter=',')
