# -*- coding: utf-8 -*-
from OSMPythonTools.overpass import Overpass
import numpy as np
import pandas as pd

overpass = Overpass()


df = pd.read_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_GS_skip_freetime_3.csv')

tmp=1
mapinf=[0]
for j in range(len(df)):
    tmp=1
    print(j)
    #result = overpass.query('node[~"^(highway)$"~"."](around:50,23.562812, 120.475344);out;')
    if(j%1000==0):
        result = overpass.query('node["highway"= "crossing"](around:5000,'+str(df['lati'][j])+', '+str(df['long'][j])+');out;')
    for i in range(len(result.elements())):
        if((abs(result.elements()[i].lat()-df['lati'][j])**2 + abs(result.elements()[i].lon()-df['long'][j])**2)**0.5<0.0005):
            print("agree")
            if((abs(result.elements()[i].lat()-df['lati'][j])**2 + abs(result.elements()[i].lon()-df['long'][j])**2)**0.5<tmp):
                tmp=(abs(result.elements()[i].lat()-df['lati'][j])**2 + abs(result.elements()[i].lon()-df['long'][j])**2)**0.5
            #break
        '''
        if(result.elements()[i].tags()=={'highway': 'crossing'}):
            print("agree")
            tmp=1
            break
        '''
    mapinf.append(tmp)

df["map_inf"]=mapinf[1:]
df.to_csv('data/can_Internal_difference/static_IMU/multiprocess/0609_out/after_GS_skip_freetime_3.csv', index = False)
