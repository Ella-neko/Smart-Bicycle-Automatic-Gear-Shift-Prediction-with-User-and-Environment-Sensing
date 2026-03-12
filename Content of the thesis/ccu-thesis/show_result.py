# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 16:28:58 2021

@author: chengxue
"""
from numpy import genfromtxt
import matplotlib.pyplot as plt


lgbm = genfromtxt('image/oneSensor/XGB/OutsideOnlyRate.csv', delimiter=',')
#cat = genfromtxt('Result/outside/CAT.csv', delimiter=',')
#rf = genfromtxt('Result/outside/RF.csv', delimiter=',')
#xgb = genfromtxt('Result/outside/XGB.csv', delimiter=',')
gt = genfromtxt('outsideGT.csv', delimiter=',')


plt.figure()
#plt.plot(range(test_size), df['Gear'][-test_size:])
plt.plot(range(gt.shape[0]),gt)
plt.plot(range(gt.shape[0]), lgbm)
#plt.plot(range(gt.shape[0]),cat)
#plt.plot(range(gt.shape[0]),rf)
#plt.plot(range(gt.shape[0]),xgb)


plt.legend(['ground turth','predict'],loc = 1)
plt.ylabel('gear')
plt.xlabel('time');
plt.show()

lgbm = genfromtxt('image/oneSensor/XGB/SchoolOnlyPRIMU.csv', delimiter=',')
#cat = genfromtxt('Result/school/CAT.csv', delimiter=',')
#rf = genfromtxt('Result/school/RF.csv', delimiter=',')
#xgb = genfromtxt('Result/school/XGB.csv', delimiter=',')
gt = genfromtxt('schoolGT.csv', delimiter=',')

plt.figure()
#plt.plot(range(test_size), df['Gear'][-test_size:])
plt.plot(range(gt.shape[0]),gt)
plt.plot(range(gt.shape[0]), lgbm)
#plt.plot(range(gt.shape[0]),cat)
#plt.plot(range(gt.shape[0]),rf)
#plt.plot(range(gt.shape[0]),xgb)


plt.legend(['ground turth','predict'],loc = 1)
plt.ylabel('gear')
plt.xlabel('time');
plt.show()
