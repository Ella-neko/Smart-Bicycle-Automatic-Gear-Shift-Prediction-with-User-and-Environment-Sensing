# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 16:28:58 2021

@author: chengxue
"""
from numpy import genfromtxt
import matplotlib.pyplot as plt
import numpy as np


lgbm = genfromtxt('image/NNtest/outside_pastgear.csv', delimiter=',')
#cat = genfromtxt('Result/outside/CAT.csv', delimiter=',')
#rf = genfromtxt('Result/outside/RF.csv', delimiter=',')
#xgb = genfromtxt('Result/outside/XGB.csv', delimiter=',')
gt = genfromtxt('outsideGT.csv', delimiter=',')


test_size=int(lgbm.size/6);
test_gear=np.zeros(test_size)
y_val=lgbm
slide_size=5
change_feq=0
change_score=0
for i in range(test_size):
    test_gear[i]=np.array(y_val[i]).argmax()+1
    '''
    diff = np.abs(np.array(y_val[i])-np.array(y_test[i]))
    print(diff)
    #print(f'{i+1:2}. {y_val[i]:8.4f} {y_test[i]:8.4f} {diff:8.4f}')
    '''

plt.figure()
#plt.plot(range(test_size), df['Gear'][-test_size:])
plt.plot(range(gt.shape[0]),gt)
plt.plot(range(gt.shape[0]), test_gear)
#plt.plot(range(gt.shape[0]),cat)
#plt.plot(range(gt.shape[0]),rf)
#plt.plot(range(gt.shape[0]),xgb)


plt.legend(['ground turth','predict'],loc = 1)
plt.ylabel('gear')
plt.xlabel('time');
plt.show()



lgbm = genfromtxt('image/NNtest/204080160.csv', delimiter=',')
#cat = genfromtxt('Result/school/CAT.csv', delimiter=',')
#rf = genfromtxt('Result/school/RF.csv', delimiter=',')
#xgb = genfromtxt('Result/school/XGB.csv', delimiter=',')
gt = genfromtxt('schoolGT.csv', delimiter=',')


test_size=int(lgbm.size/6);
test_gear=np.zeros(test_size)
y_val=lgbm
slide_size=5
change_feq=0
change_score=0
for i in range(test_size):
    test_gear[i]=np.array(y_val[i]).argmax()+1
    '''
    diff = np.abs(np.array(y_val[i])-np.array(y_test[i]))
    print(diff)
    #print(f'{i+1:2}. {y_val[i]:8.4f} {y_test[i]:8.4f} {diff:8.4f}')
    '''

plt.figure()
#plt.plot(range(test_size), df['Gear'][-test_size:])
plt.plot(range(gt.shape[0]),gt)
plt.plot(range(gt.shape[0]), test_gear[:1999])
#plt.plot(range(gt.shape[0]),cat)
#plt.plot(range(gt.shape[0]),rf)
#plt.plot(range(gt.shape[0]),xgb)


plt.legend(['ground turth','predict'],loc = 1)
plt.ylabel('gear')
plt.xlabel('time');
plt.show()
