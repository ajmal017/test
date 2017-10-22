# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 04:53:09 2017

@author: abhishek.chaturvedi
"""

import os, sys
import numpy as np
import pandas as pd
import datetime
from sortedcontainers import SortedDict

#Constants
tick_size = 1
file = '~/PycharmProjects/self/test/data/data.txt'
filemp1 = '~/PycharmProjects/self/test/data/data-mp1.txt'

df = pd.read_csv(file, names=['stock','day','timestamp','open','high','low','close','volume'])
#print df[['high','low']]
high = df.high.max()
low = df.low.min()
price_array = np.arange(low, high, tick_size)
print 'Max = ',high
print 'Min = ',low

columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','nTPO','TPO','values']
#Create the pricePoint from MAX and MIN of df and then reverse it to sort in descending order
pricePoint = np.array([np.arange(df['low'].min(), df['high'].max(), tick_size)]).T[::-1]
mp = pd.DataFrame(index=price_array, columns = columns)
mp['pricePoint'] = mp.index
#print mp
#iterate
column_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M']
n = 0
"""
for row in df.itertuples():
    h = row.high
    l = row.low
        
    mask = (mp.index <= h) & (mp.index >= l)
    _ = mp[mask]
    
    for r in _.itertuples():
        _.set_value(r.Index, column_list[n],1)
    n = n + 1
#print the dataframe
print _
"""
mp1 = mp
for row in df.itertuples():
    h = row.high
    l = row.low
    mp1.loc[(mp1.pricePoint <= h) & (mp1.pricePoint>=l), column_list[n]] = column_list[n]
    n += 1

mp1['nTPO'] = mp1.count(axis=1)
mp1.to_csv(filemp1)
#print mp1
print 'Median Price=',mp1.pricePoint.median()
print 'Total # of TPO',mp1.nTPO.cumsum().iloc[-1]
print '70% of TPO',abs(mp1.nTPO.cumsum().iloc[-1] * .7)
print 'Possible POC',mp1.nTPO.max()
print 'Maximum TPO at',mp1.nTPO.idxmax()
poc_index = mp1.nTPO.idxmax()
tpo70 = abs(mp1.nTPO.cumsum().iloc[-1] * .7)
tpo_sum = 0.
mid_flag = False
"""
while tpo_sum < tpo70:
    for i,row in mp1.iterrows():
        if mid_flag:
            tpo_sum = tpo_sum + row.nTPO
        else:
            if i == poc_index: 
                mid_flag = True
                tpo_sum = tpo_sum + row.nTPO
"""
#for i in price_array:
#    print mp1.at[i, 'nTPO']

#Create a dictionary of pricePoints and TPO at the pricePoints
tpo_price_dict = pd.Series(mp1.nTPO.values, index=mp1.pricePoint).to_dict()
counter = int(np.ceil(len(tpo_price_dict)/2))
iter = iter(range(1,counter))
down = False
up  = False
first = True
#Initialize the TPO sum to the POC TPO value
tpo_sum = tpo_price_dict[poc_index] 

for i in iter:
    print i
    if first:
        sum_down = tpo_price_dict[poc_index+i]# + tpo_price_dict[poc_index+i*2]
        sum_up = tpo_price_dict[poc_index-i]# + tpo_price_dict[poc_index-i*2]
    else:
        if down:
            sum_down = tpo_price_dict[poc_index+i]# + tpo_price_dict[poc_index+i*2]
        if up:
            sum_up = tpo_price_dict[poc_index-i]# + tpo_price_dict[poc_index-i*2]
    
    tpo_sum = max(sum_up, sum_down) + tpo_sum

    if up and sum_down == sum_up:
        down = True
        up = False
    if down and sum_down  == sum_up:
        up = True
        down = False
    
    if sum_down > sum_up:
        down = True
        up = False
        print 'At index',poc_index+i
        print 'Down -->', tpo_sum

    if sum_up > sum_down:
        down = False
        up = True
        print 'At index',poc_index-i
        print 'Up -->', tpo_sum

    if tpo_sum  > tpo70: break
    #next(iter, None)
