###import required libraries

import torch
import torch.nn as nn

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
import torchcontrib.optim

###Data load section

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
#f = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/outside_0610.csv')
#df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/add_outside_0604.csv')
df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/add_0515_0610.csv')


#df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0519_out/after_GS_skip_freetime.csv')
#df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/out_test_0521.csv')
#df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/test_0521_2000.csv')
df_t = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/mix/outside_test_0604.csv')


print(df.head())

#print(df['pickup_datetime'].describe())


###Calculate the distance traveled

def haversine_distance(df, lat1, long1, lat2, long2):
    """
    Calculates the haversine distance between 2 sets of GPS coordinates in df
    """
    r = 6371  # average radius of Earth in kilometers

    phi1 = np.radians(df[lat1])
    phi2 = np.radians(df[lat2])

    delta_phi = np.radians(df[lat2] - df[lat1])
    delta_lambda = np.radians(df[long2] - df[long1])

    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = (r * c)  # in kilometers
    return d


#df['dist_km'] = haversine_distance(df,'pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude')
#print(df.head())        
###Add a datetime column and derive usefull statistics
'''
df['EDTdate'] = pd.to_datetime(df['pickup_datetime'].str[:19]) - pd.Timedelta(hours=4)
df['Hour'] = df['EDTdate'].dt.hour
df['AMorPM'] = np.where(df['Hour']<12,'am','pm')
df['Weekday'] = df['EDTdate'].dt.strftime("%a")
print(df.head())

print(df['EDTdate'].min())
print(df['EDTdate'].max())
'''
##seperate categorical and continuos columns

print(df.columns)

cat_cols = ['Hour', 'AMorPM', 'Weekday']
cont_cols = ['lati', 'long','Gyro', 'Rate', 'Pressure', 'Heartbeat','Temp','map_inf']
#cont_cols = ['lati', 'long','Gyro', 'Rate', 'Pressure', 'Heartbeat','Temp']
#cont_cols = ['lati', 'long', 'Rate', 'Heartbeat', 'Pressure','Temp']
#cont_cols = ['lati', 'long', 'Rate', 'Pressure', 'Heartbeat','Temp','map_inf']
#cont_cols = ['Gyro', 'Rate', 'Pressure']

y_col = ['Gear']  # this column contains the labels
print(cat_cols)


###Convert our three categorical columns to category dtypes.
'''
for cat in cat_cols:
    df[cat] = df[cat].astype('category')
print(df.dtypes)

print(df['Hour'].head())
print(df['AMorPM'].head())
print(df['AMorPM'].cat.categories)
print(df['AMorPM'].head().cat.codes)
print(df['Weekday'].cat.categories)
print(df['Weekday'].head().cat.codes)


##Now we want to combine the three
# categorical columns into one input
# array using numpy.stack We don't want the Series index,
# just the values.

hr = df['Hour'].cat.codes.values
ampm = df['AMorPM'].cat.codes.values
wkdy = df['Weekday'].cat.codes.values

cats = np.stack([hr, ampm, wkdy], 1)

print(cats[:5])

###convert numpy arrays to tensor

cats = torch.tensor(cats, dtype=torch.int64)
# this syntax is ok, since the source data is an array, not an existing tensor

print(cats[:5])
'''
###convert continuosu variables to a sensor

conts_t = np.stack([df_t[col].values for col in cont_cols], 1)
conts = np.stack([df[col].values for col in cont_cols], 1)
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

#--past gps----
conts_t = np.c_[ conts_t, np.zeros(df_t.index.stop)]
conts_t = np.c_[ conts_t, np.zeros(df_t.index.stop)]
conts=np.c_[ conts, np.zeros(df.index.stop)]
conts=np.c_[ conts, np.zeros(df.index.stop)]


conts_t[0,-2:]=conts_t[0,:2]
conts[0,-2:]=conts[0,:2]

conts_t[1:,-2:]=conts_t[:-1,:2]
conts[1:,-2:]=conts[:-1,:2]
#--past gps end----
'''

conts_t = np.c_[ conts_t, np.zeros(df_t.index.stop)+2]
conts=np.c_[ conts, np.zeros(df.index.stop)+2]


conts_t[:,:-1]=(conts_t[:,:-1]-conts[:,:-1].mean(0))/conts[:,:-1].std(0) # feature scaling
conts[:,:-1]=(conts[:,:-1]-conts[:,:-1].mean(0))/conts[:,:-1].std(0) # feature scaling


'''
for i in range(1,df.index.stop):
    conts[i][7]= int(df['Gear'][i-1])
'''
#conts=np.c_[ conts, df['Gear'][1:df.index.stop].values]
conts_t = torch.tensor(conts_t, dtype=torch.float)

conts = torch.tensor(conts, dtype=torch.float)
print(conts[:5])


### Convert labels to a tensor test
y_t=[]
for i in range(0,int(df_t.index.stop)):
    if(df_t['Gear'][i]==1):
        y_t.append([1, 0, 0, 0, 0, 0])
    elif(df_t['Gear'][i]==2):
        y_t.append([0, 1, 0, 0, 0, 0])
    elif(df_t['Gear'][i]==3):
        y_t.append([0, 0, 1, 0, 0, 0])
    elif(df_t['Gear'][i]==4):
        y_t.append([ 0, 0, 0, 1, 0,0])
    elif(df_t['Gear'][i]==5):
        y_t.append([0, 0, 0, 0, 1, 0])
    elif(df_t['Gear'][i]==6):
        y_t.append([0, 0, 0, 0, 0, 1])
        
y_t = torch.tensor(y_t, dtype=torch.float)

### Convert labels to a tensor
y=[]
for i in range(0,int(df.index.stop)):
    if(df['Gear'][i]==1):
        y.append([1, 0, 0, 0, 0, 0])
    elif(df['Gear'][i]==2):
        y.append([0, 1, 0, 0, 0, 0])
    elif(df['Gear'][i]==3):
        y.append([0, 0, 1, 0, 0, 0])
    elif(df['Gear'][i]==4):
        y.append([ 0, 0, 0, 1, 0,0])
    elif(df['Gear'][i]==5):
        y.append([0, 0, 0, 0, 1, 0])
    elif(df['Gear'][i]==6):
        y.append([0, 0, 0, 0, 0, 1])
        
#y = torch.tensor(y, dtype=torch.float).reshape(-1,1)
y = torch.tensor(y, dtype=torch.float)
#y=y.numpy()


print(y[:5])

#print(cats.shape)
print(conts.shape)
#print(y.shape)


###set an embedding size

#The rule of thumb for determining the embedding size is to
#divide the number of unique entries in each column by 2, but not to exceed 50.

# This will set embedding sizes for Hours, AMvsPM and Weekdays
#cat_szs = [len(df[col].cat.categories) for col in cat_cols]
#emb_szs = [(size, min(50, (size+1)//2)) for size in cat_szs]
#print(emb_szs)



###define a tabular Model
#This somewhat follows the fast.ai library The goal is to define a model
# based on the number of continuous columns (given by conts.shape[1]) plus
# the number of categorical columns and their embeddings (given by len(emb_szs)
# and emb_szs respectively). The output would either be a regression (a single
# float value), or a classification (a group of bins and their softmax values).
# For this exercise our output will be a single regression value. Note that
# we'll assume our data contains both categorical and continuous data. You
# can add boolean parameters to your own model class to handle a variety of
# datasets
gear_num=5

class TabularModel(nn.Module):

    def __init__(self,  n_cont, out_sz, layers, p):
        super().__init__()
        
        '''
        self.embeds = nn.ModuleList([nn.Embedding(ni, nf) for ni, nf in emb_szs])
        self.emb_drop = nn.Dropout(p)
        self.bn_cont = nn.BatchNorm1d(n_cont)

        #layerlist = []
        n_emb = sum((nf for ni, nf in emb_szs))
        
        n_in = n_emb + n_cont
        '''
        #n_in = n_cont
        #self.lstm = nn.LSTM(n_in, layers[0], 1)
        #n_in=layers[0]
        self.layer1 = nn.Linear(  n_cont+gear_num, layers[0])
        self.ReLU1 = nn.ReLU(inplace=True)
        self.BatchNorm1d1 = nn.BatchNorm1d(layers[0])
        #self.GroupNorm1d1 = nn.GroupNorm(25, layers[0])
        #n_in=layers[1]
        self.layer2 = nn.Linear(layers[0]+n_cont+gear_num, layers[1])
        #self.layer2 = nn.Linear(layers[0]+3, layers[1])
        self.ReLU2 = nn.ReLU(inplace=True)
        self.BatchNorm1d2 = nn.BatchNorm1d(layers[1])
        #self.GroupNorm1d2 = nn.GroupNorm(25, layers[1])
        
        self.layer3 = nn.Linear(layers[1]+layers[0]+gear_num, layers[2])
        #self.layer3 = nn.Linear(layers[1]+3, layers[2])
        self.ReLU3 = nn.ReLU(inplace=True)
        self.BatchNorm1d3 = nn.BatchNorm1d(layers[2])
        
        self.layer4 = nn.Linear(layers[2]+layers[1]+gear_num, layers[3])
        #self.layer4 = nn.Linear(layers[2]+3, layers[3])
        self.ReLU4 = nn.ReLU(inplace=True)
        self.BatchNorm1d4 = nn.BatchNorm1d(layers[3])
        
        self.layer5 = nn.Linear(layers[3]+layers[2]+gear_num, layers[4])
        self.ReLU5 = nn.ReLU(inplace=True)
        self.BatchNorm1d5 = nn.BatchNorm1d(layers[4])
        
        
        self.layer6 = nn.Linear(layers[4]+layers[3]+gear_num, layers[5])
        #self.layer3 = nn.Linear(layers[1]+3, layers[2])
        self.ReLU6 = nn.ReLU(inplace=True)
        self.BatchNorm1d6 = nn.BatchNorm1d(layers[5])
        
        self.layer7 = nn.Linear(layers[5]+layers[4]+layers[1]+gear_num, layers[6])
        #self.layer3 = nn.Linear(layers[1]+3, layers[2])
        self.ReLU7 = nn.ReLU(inplace=True)
        self.BatchNorm1d7 = nn.BatchNorm1d(layers[6])
        
        self.layer8 = nn.Linear(layers[6]+layers[5]+layers[0]+gear_num, layers[7])
        #self.layer3 = nn.Linear(layers[1]+3, layers[2])
        self.ReLU8 = nn.ReLU(inplace=True)
        self.BatchNorm1d8 = nn.BatchNorm1d(layers[7])
        
        self.layer9 = nn.Linear(layers[7]+layers[6]+n_cont+gear_num, layers[8])
        #self.layer3 = nn.Linear(layers[1]+3, layers[2])
        self.ReLU9 = nn.ReLU(inplace=True)
        self.BatchNorm1d9 = nn.BatchNorm1d(layers[8])
        
        self.Dropout = nn.Dropout(p)
        '''
        for i in layers:
            layerlist.append(nn.Linear(n_in, i))
            layerlist.append(nn.ReLU(inplace=True))
            layerlist.append(nn.BatchNorm1d(i))
            layerlist.append(nn.Dropout(p))
            n_in = i
        '''
        self.fc = nn.Linear(layers[-1], out_sz)
        self.softmax = nn.Softmax(dim=1)
        self.tanh = nn.Tanh()
        self.sigmoid = nn.Sigmoid()
        '''
        layerlist.append(nn.Linear(layers[-1], out_sz))
        layerlist.append(nn.Softmax(dim=1))
        self.layers = nn.Sequential(*layerlist)
        '''

    def forward(self, x_cont):
        '''
        embeddings = []
        for i, e in enumerate(self.embeds):
            #print("e")
            #print(e)
            #print(i)
            embeddings.append(e(x_cat[:, i]))
        x = torch.cat(embeddings, 1)
        x = self.emb_drop(x)

        x_cont = self.bn_cont(x_cont)
        x = torch.cat([x, x_cont], 1)
        '''
        #h_0 = y.data.new(2,x_cont.size(0),100).fill_(0).float()
        #c_0 = y.data.new(2,x_cont.size(0),100).fill_(0).float()
        #y,(ht,ct) = self.lstm(x_cont)
        #y = torch.cat((x_cont,x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8]),1)
        y = x_cont
        for ii in range(gear_num):
            y = torch.cat((y,x_cont[:,-1:]),1)
        #x_cont = y
        y = self.layer1(y)
        y = self.ReLU1(y)
        y = self.BatchNorm1d1(y)
        #y = self.GroupNorm1d1(y)
        #y = self.Dropout(y)
        #y1=torch.cat((y,x_cont,x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8]),1)
        
        
        y1=torch.cat((y,x_cont),1)
        #y1=y
        for ii in range(gear_num):
            y1 = torch.cat((y1,x_cont[:,-1:]),1)
        #y1=torch.cat((y,x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8]),1)
        y1 = self.layer2(y1)
        y1 = self.ReLU2(y1)
        y1 = self.BatchNorm1d2(y1)
        #y = self.GroupNorm1d2(y)
        #y1 = self.Dropout(y1)
        #y2=torch.cat((y1,y,x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8]),1)
        
        y2=torch.cat((y1,y),1)
        #y2=y1
        
        for ii in range(gear_num):
            y2 = torch.cat((y2,x_cont[:,-1:]),1)
        #y2=torch.cat((y1,x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8]),1)
        y2 = self.layer3(y2)
        y2 = self.ReLU3(y2)
        y2 = self.BatchNorm1d3(y2)
        y2 = self.Dropout(y2)
        
        y3=torch.cat((y2,y1),1)
        #y3=y2
        for ii in range(gear_num):
            y3 = torch.cat((y3,x_cont[:,-1:]),1)
        #y3=torch.cat((y2,x_cont[:,7:8],x_cont[:,7:8],x_cont[:,7:8]),1)
        y3 = self.layer4(y3)
        y3 = self.ReLU4(y3)
        y3 = self.BatchNorm1d4(y3)
        #y3 = self.Dropout(y3)
        
        y4=torch.cat((y3,y2),1)
        #y4=y3
        for ii in range(gear_num):
            y4 = torch.cat((y4,x_cont[:,-1:]),1)
        y4 = self.layer5(y4)
        y4 = self.ReLU5(y4)
        y4 = self.BatchNorm1d5(y4)
        #y4 = self.Dropout(y4)
        
        y5=torch.cat((y4,y3),1)
        for ii in range(gear_num):
            y5 = torch.cat((y5,x_cont[:,-1:]),1)
        y5 = self.layer6(y5)
        y5 = self.ReLU6(y5)
        y5 = self.BatchNorm1d6(y5)
        #y5 = self.Dropout(y5)

        
        y6=torch.cat((y5,y4,y1),1)
        for ii in range(gear_num):
            y6 = torch.cat((y6,x_cont[:,-1:]),1)
        y6 = self.layer7(y6)
        y6 = self.ReLU7(y6)
        y6 = self.BatchNorm1d7(y6)
        y6 = self.Dropout(y6)
        
        y7=torch.cat((y6,y5,y),1)        
        for ii in range(gear_num):
            y7 = torch.cat((y7,x_cont[:,-1:]),1)
        y7 = self.layer8(y7)
        y7 = self.ReLU8(y7)
        y7 = self.BatchNorm1d8(y7)
        #y7 = self.Dropout(y7)
        
        y8=torch.cat((y7,y6,x_cont),1)
        for ii in range(gear_num):
            y8 = torch.cat((y8,x_cont[:,-1:]),1)
        y8 = self.layer9(y8)
        y8 = self.ReLU9(y8)
        y8 = self.BatchNorm1d9(y8)
        
        #y=torch.cat((y,x_cont[:,7:8]),1)
        #y=torch.cat((y8,x_cont),1) 
        #y = self.Dropout(y8)
        y = self.fc(y8)
        #y = self.tanh(y)
        #y = self.sigmoid(y) 
        y = self.softmax(y)
        
        return y


#torch.manual_seed(33)

use_gpu = torch.cuda.is_available()
model = TabularModel( conts.shape[1], 6, [40,80,80,160,160,160,80,80,40], p=0.4)
#model = TabularModel( conts.shape[1], 6, [20,20,40,40,80,40,40,20,20], p=0.5)

#model.cuda(0)
print(model)

###define loss function and optimizer

#PyTorch does not offer a built-in RMSE Loss
# function, and it would be nice to see this in place of MSE.
#For this reason, we'll simply apply the torch.sqrt() function to the output
# of MSELoss during training.

#criterion = nn.MSELoss()  # we'll convert this to RMSE later
#criterion = nn.NLLLoss()
#criterion = nn.MultiLabelSoftMarginLoss()
criterion = nn.CrossEntropyLoss()
#optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
#optimizer = torchcontrib.optim.SWA(sub_optimizer, swa_freq=1500)

#optimizer = torch.optim.SGD(model.parameters(), lr=0.001,weight_decay=0.0005)

#optimizer = torch.optim.RMSprop(model.parameters(), lr=0.001)

if(use_gpu):
    model = model.cuda()
    criterion = criterion.cuda()
    #optimizer = optimizer.cuda()
###perform train , test splits

#At this point our batch size is the entire dataset of 120,000 records. This will take a long time to train, so you might consider reducing t
# his. We'll use 60,000. Recall that our tensors are already randomly shuffled.

#batch_size = 100
test_size = int(df_t.index.stop)
#test_size=2000;
'''
if(test_size>4000):
    test_size=4000

cat_train = cats[:-test_size]
cat_test = cats[-test_size:]
'''

#con_train = conts[:-test_size]
con_train = conts[:]
#con_test = conts[-test_size:]
con_test = conts_t[0:]

#y_train = y[:-test_size]
y_train = y[:]
#y_test = y[-test_size:]
y_test = y_t[0:]

if(use_gpu):
    con_train = con_train.cuda()
    con_test = con_test.cuda()
    y_train = y_train.cuda()
    y_test = y_test.cuda()

'''
cat_train = cats[:batch_size-test_size]
cat_test = cats[batch_size-test_size:batch_size]

con_train = conts[:batch_size-test_size]
con_test = conts[batch_size-test_size:batch_size]

y_train = y[:batch_size-test_size]
y_test = y[batch_size-test_size:batch_size]

print(len(cat_train))
print(len(cat_test))
'''
'''
a = torch.max(y_train,1)[1].clone()
con_train = con_train.numpy()
#con_train[j][7]
for j in range(1,df.index.stop-test_size):
    con_train[j][7]=a[j-1].numpy()
        
con_train = torch.tensor(con_train, dtype=torch.float)
'''
##Train the model

import time

start_time = time.time()

epochs = 30000
batch = 20
losses = []
#gc.enable()
model.train()
#model.eval()

gamma=0.1
lr=0.1
for i in range(epochs):
    optimizer.zero_grad()

    #i += 1
    con_train_buffer=np.zeros((batch,8))
    #y_pred = torch.zeros(df.index.stop-test_size,6)
    y_pred = torch.zeros(df.index.stop,6)
    '''
    for j in range(int((df.index.stop-test_size)/batch)):
        con_train_buffer=np.zeros((batch,8))    
        con_train_buffer[0:batch,:]=con_train[j*batch:(j+1)*batch].clone()
        #print(con_train_buffer)
        #con_train_buffer = torch.Tensor((con_train_buffer))
        y_pred_buffer = model(cat_train[j],torch.Tensor((con_train_buffer)))
        y_pred[j*batch:(j+1)*batch,:]=torch.clone(y_pred_buffer)
        if(j<int((df.index.stop-test_size)/batch)-1):
            for z in range (batch):
                con_train[(j+1)*batch+z][7]= torch.max(y_pred_buffer,1)[1][z]
            #con_train[(j+1)*batch:(j+2)*batch][7]= torch.max(y_pred_buffer,1)[1]
    
      '''
    #mem2 = proc.get_memory_info().rss
    #gc.collect
    #mem3 = proc.get_memory_info().rss
    #print(y_pred)
    '''
    gamma=0.1
    lr=0.001
    
    if(i==int(epochs*0.625)):
        lr = lr * (gamma)
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr
    '''     
    if(i==int(epochs*0.2) or i==int(epochs*0.4)):
    #if(i==6000 or i==12000):
        lr = lr * (gamma)
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr
    y_pred = model(con_train)
    
    
    #for j in range(1,df.index.stop-test_size):
    
        
    a = torch.max(y_pred,1)[1].clone()
    if(use_gpu):
        con_train = con_train.cpu()
        a = a.cpu()
        
    con_train = con_train.numpy()
    #con_train[j][7]
    for j in range(1,df.index.stop-test_size):
    #for j in range(1,df.index.stop):
        con_train[j][-1]=a[j-1].numpy()
        
    con_train = torch.tensor(con_train, dtype=torch.float)
    
    loss = criterion(y_pred,torch.max(y_train,1)[1])  # loss
    losses.append(loss)
    
    #conts[i][7]= int(df['Gear'][i-1])
    '''
    # a neat trick to save screen space:
    if i % 25 == 1:
        print(f'epoch: {i:3}  loss: {loss.item():10.8f}')
    
    optimizer.zero_grad()
    #loss.backward()
    
    #with torch.no_grad():
    y_val = model(cat_test, con_test)
    loss = torch.sqrt(criterion(y_val,torch.max( y_test,1)[1] ))
    '''
    
    if(use_gpu):
        con_train = con_train.cuda()
        a = a.cuda()
        
    loss.backward()
    optimizer.step()
    print(f'epoch: {i:3}  loss: {loss.item():10.8f}')
    #print(f'RMSE: {loss:.8f}')
print(f'epoch: {i:3}  loss: {loss.item():10.8f}')  # print the last line
print(f'\nDuration: {time.time() - start_time:.0f} seconds')  # print the time elapsed

#optimizer.swap_swa_sgd()


'''
###plot the loss function
plt.figure()
plt.plot(range(epochs), losses)
plt.ylabel('RMSE Loss')
plt.xlabel('epoch');
plt.show()
'''

##validate the model

#Here we want to run the entire test set through the model, and compare it to the known labels.
#For this step we don't want to update weights and biases, so we set torch.no_grad()

#model.layer1.weight[:,7]=model.layer1.weight[:,7]*1.5
model.eval()
with torch.no_grad():
    
    y_val= torch.zeros(test_size,6)
    for j in range(test_size):
        if(use_gpu):
            con_test = con_test.cpu()
        con_val_buffer=np.zeros((1,conts.shape[1]))
        con_val_buffer[0]=con_test[j].clone()
        #print(con_train_buffer)
        #con_train_buffer = torch.Tensor((con_train_buffer))
        
        
        con_val_buffer = torch.from_numpy(con_val_buffer)
        if(use_gpu):
            con_val_buffer = con_val_buffer.cuda()
        
        y_pred_buffer = model((con_val_buffer).float())
        
        
        y_val[j,:]=torch.clone(y_pred_buffer)
        
        if(use_gpu):
            con_test = con_test.cuda()
        
        if(j<test_size-1):
            con_test[j+1][-1]= torch.max(y_pred_buffer,1)[1]
            #con_train[(j+1)*batch:(j+2)*batch][7]= torch.max(y_pred_buffer,1)[1]
    
    #y_val = model(con_test)
    if(use_gpu):
        y_test = y_test.cpu()
    #loss = criterion(y_val, torch.max(y_test,1)[1])
print(f'RMSE: {loss:.8f}')


#Now let's look at the first 50 predicted values:
y_val= y_val.numpy().tolist()
print(y_val)
print(y_test)
#print(f'{"PREDICTED":>12} {"ACTUAL":>8} {"DIFF":>8}')

#test_size=2000

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
    
    if(i+slide_size<test_size):
        change_feq=0
        for j in range(slide_size):
            if(np.array(y_val[i+j]).argmax()!=np.array(y_val[i+j+1]).argmax()):
                change_feq=change_feq+1
    if(change_feq>=int(slide_size*0.5)):
        change_score=change_score-change_feq
        
    if(np.array(y_val[i]).argmax()==np.array(y_test[i]).argmax()):
        test_count[0]=test_count[0]+1
        #test_count=test_count+1
    elif(abs(np.array(y_val[i]).argmax()-np.array(y_test[i]).argmax())==1):
        test_count[1]=test_count[1]+1
    elif(abs(np.array(y_val[i]).argmax()-np.array(y_test[i]).argmax())==2):
        test_count[2]=test_count[2]+1
    elif(abs(np.array(y_val[i]).argmax()-np.array(y_test[i]).argmax())==3):
        test_count[3]=test_count[3]+1
    elif(abs(np.array(y_val[i]).argmax()-np.array(y_test[i]).argmax())==4):
        test_count[4]=test_count[4]+1
    elif(abs(np.array(y_val[i]).argmax()-np.array(y_test[i]).argmax())==5):
        test_count[5]=test_count[5]+1
    else:
        test_er=test_er+(np.array(y_val[i]).argmax()-np.array(y_test[i]).argmax())**2
    test_gear[i]=np.array(y_val[i]).argmax()+1
    '''
    diff = np.abs(np.array(y_val[i])-np.array(y_test[i]))
    print(diff)
    #print(f'{i+1:2}. {y_val[i]:8.4f} {y_test[i]:8.4f} {diff:8.4f}')
    '''
    


print(test_count[:]/test_size)
print("scoure:",test_count[0]/test_size+change_score/test_size)

plt.plot(range(test_size), test_gear[:])
plt.legend(['ground turth','predict'],loc = 1)
plt.ylabel('gear')
plt.xlabel('time');
plt.show()

gap = ['0', '1', '2', '3','4','5']
x = np.arange(len(gap))
plt.bar(x, test_count[:]/test_size, color=['green'])
plt.xticks(x, gap)
plt.xlabel('gap level')
plt.ylabel('percentage')
plt.title('Gap percentage')
for x,y in enumerate(test_count[:]/test_size):plt.text(x,y,'%.3f'%y,ha='center')
plt.show()

np.savetxt('XGB_outside.csv',y_val, delimiter=',')

#So while many predictions were off by a few cents, some
# were off by $19.00. Feel free to change the batch size, test size,
# and number of epochs to obtain a better model.