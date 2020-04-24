#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 14:45:51 2020

@author: planetmaker
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

filename = "~/PowerFolders/ICAPS_data_analysis/Housekeeping/log_1000Hz_15112019_113621.csv"

df = pd.read_csv(filename, sep=';') # , index_col='time_stamp')

#df.plot(kind='scatter', x='time_stamp', y='Icm1', color='red', ax=ax)
#df.plot(kind='scatter', x='time_stamp', y='Icm2', color='blue', ax=ax)
#ax2 = ax.twinx()
#
#df.plot(kind='scatter', x='time_stamp', y='Uvm1', color='navy', ax=ax2)

print(df['oos2'])

count = 0
current = 0
for val in df['oos2']:
    if val != current:
        count = count + 1
        current = val
print("Number of OOS image trigger changes / trigger highs encountered: ",count, count/2)

print(sum(df['ldm']))

#current = 0
#for timestamp,val in zip(df['time_stamp'], df['Icm1']):
#    aval = abs(val)
#    if (aval > 0.05 and current < 0.05):
#        startt = timestamp
#        current = aval
#    if (aval < 0.05 and current > 0.05):
#        print(startt, ' ... ', timestamp)
#        current = aval


imgcalib = pd.read_excel('~/PowerFolders/ICAPS_data_analysis/ICAPS_event_timeline_20200423.xlsx') 

#print(imgcalib)
#calib = []
#for timestamp,oosimg in zip(imgcalib['time_stamp'],imgcalib['OOS image#']):
#    if (timestamp is not null) and (oosimg is not null):
#        calib.append((timestamp,oosimg))
calib = imgcalib[imgcalib.time_stamp.notnull()]
calib = calib[calib['OOS image#'].notnull()]
n_OOS_images = 18437
# dOOSdt = n_OOS_images / (list(calib['time_step'])[-1] - list(calib['time_step'])[0])

#print(list(calib['time_stamp'])[-1])

oos_images_per_timestep = n_OOS_images / (list(calib['time_stamp'])[-1] - list(calib['time_stamp'])[0])
print('Average OOS images per timestep: ',oos_images_per_timestep)

print('Calibration points time_stamp to OOS image# from event timeline excel file:')
print('t0 ... t1                   (OOS#0 - OOS#1):     images/time_step')
first = 1
for t,img in zip(calib['time_stamp'],calib['OOS image#']):
    if first == 1:
        first = 0
        last_t = t
        last_img = img
        continue
    print(last_t, ' - ',t, '(',last_img, ' _ ',img,'): ',(img-last_img) / (t-last_t))
    last_t = t
    last_img = img

    
fig,ax1 = plt.subplots()

ax1.set_xlabel('time [ms]')
ax1.set_ylabel('current [au]')
ax1.plot(df['time_stamp'], df['Icm1'], color='red')
ax1.plot(df['time_stamp'], df['Icm2'], color='lightcoral')
ax1.plot(df['time_stamp'], df['Icm3'], color='darkred')
ax1.plot(df['time_stamp'], df['Icm4'], color='chocolate')
ax1.plot(df['time_stamp'], df['Icm5'], color='darkorange')
ax1.plot(df['time_stamp'], df['Icm6'], color='tan')
ax1.legend()

ax2 = ax1.twinx()

ax2.set_ylabel('U rings')
ax2.plot(df['time_stamp'], df['Uvm1'], color='blue')
ax2.plot(df['time_stamp'], df['Uvm2'], color='navy')
ax2.legend()
#
#def filter_by_t(seq, val):
#    for el in seq:
#        if el.attribute > val: yield el
#
#def time2oosimg(X):
#    global calib
#    print(calib)
#    global n_OOS_images
#    return (X - list(calib['time_stamp'])[0]) * dOOSdt
#
#def oosimg2time(X):
#    return X
##
#
#def oos_ticks_function(X):
#    global calib
#    global n_OOS_images
#    listt = list(calib['time_step']) - X
#    lastt = filter_by_t(listt, X)
#    print('Lastt: ', lastt)
#    return  X


#oos_ticks, labels = ax1.ticks()

#
#secx = ax1.secondary_xaxis('top', functions=(time2oosimg, oosimg2time))
#secx.set_xlabel('OOS image #')

fig.tight_layout()
plt.show()
