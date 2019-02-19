#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 22:37:22 2019

@author: planetmaker
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calibrate_axis(timeline, minus_start, minus_end, null_start, null_end, plus_start, plus_end):
    minus_vec = timeline[minus_start:minus_end]
    null_vec  = timeline[null_start:null_end]
    plus_vec  = timeline[plus_start:plus_end]
    
    minus = (np.mean(minus_vec), np.std(minus_vec))
    null  = (np.mean(null_vec), np.std(null_vec))
    plus  = (np.mean(plus_vec), np.std(plus_vec))
    
    return (minus, null, plus)

def read_sensor_file(filename):
    sensor_arr = pd.read_csv(filename, sep='\t', header=2, decimal=',', names=['x','y','z'])
    return sensor_arr

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


f_logging = 400
# calibration
cal_filename = '/home/planetmaker/Bilder/dtc_201902/calibration_20190218.txt'
t_z_plus = [0*f_logging, 10*f_logging]
t_z_minus = [21*f_logging, 27*f_logging]
t_y_plus = [40*f_logging, 55*f_logging]
t_y_minus = [64*f_logging, 72*f_logging]
t_x_plus = [77*f_logging, 83*f_logging]
t_x_minus = [89*f_logging, 95*f_logging]

print('Calibration data:')
cal_data = read_sensor_file(cal_filename)

print('z: ',calibrate_axis(cal_data['z'], t_z_minus[0], t_z_minus[1], t_y_minus[0], t_y_minus[1], t_z_plus[0], t_z_plus[1]))



# drop07
#acc_filename = '/home/planetmaker/Bilder/dtc_201902/drop07/acc_drop07.txt'
#t_pre_spin = [1500*f_logging,1575*f_logging]
#t_spin = [1600*f_logging,1675*f_logging]
#t_0g   = [1693*f_logging,1695*f_logging]

# drop08
acc_filename = '/home/planetmaker/Bilder/dtc_201902/drop08/acc-data/drop08.txt'
t_pre_spin = [1485*f_logging,1510*f_logging]
t_spin = [1540*f_logging,1552*f_logging]
t_0g   = [1557*f_logging,1559*f_logging]

acc_data = read_sensor_file(acc_filename)


time = [t/400 for t in range(0,len(acc_data['x']))]

# Create plots with pre-defined labels.
fig, ax = plt.subplots()
ax.plot(time, acc_data['x'], 'k--', label='x')
ax.plot(time, acc_data['y'], 'b:', label='y')
ax.plot(time, acc_data['z'], 'r', label='z')

smooth_x = smooth(acc_data['x'],50)
smooth_y = smooth(acc_data['y'],50)
smooth_z = smooth(acc_data['z'],50)

print('Values for 1g:')
prespin = acc_data[:][t_pre_spin[0]:t_pre_spin[1]]
print('x = {} +- {}'.format(np.mean(prespin['x']),np.std(prespin['x'])))
print('y = {} +- {}'.format(np.mean(prespin['y']),np.std(prespin['y'])))
print('z = {} +- {}'.format(np.mean(prespin['z']),np.std(prespin['z'])))

print('Values for 1g with centrifuge:')
spin = acc_data[:][t_spin[0]:t_spin[1]]
print('x = {} +- {} ({}..{})'.format(np.mean(spin['x']),np.std(spin['x']), np.min(smooth_x), np.max(smooth_x)))
print('y = {} +- {} ({}..{})'.format(np.mean(spin['y']),np.std(spin['y']), np.min(smooth_y), np.max(smooth_y)))
print('z = {} +- {} ({}..{})'.format(np.mean(spin['z']),np.std(spin['z']), np.min(smooth_z), np.max(smooth_z)))

print('Values for 0g:')
nullg = acc_data[:][t_0g[0]:t_0g[1]]
print('x = {} +- {}'.format(np.mean(nullg['x']),np.std(nullg['x'])))
print('y = {} +- {}'.format(np.mean(nullg['y']),np.std(nullg['y'])))
print('z = {} +- {}'.format(np.mean(nullg['z']),np.std(nullg['z'])))
legend = ax.legend(loc='upper left', shadow=False, fontsize='x-large')

# Put a nicer background color on the legend.
#legend.get_frame().set_facecolor('C0')

plt.show()
#
#fig2, ax2 = plt.subplots()
#ax2.plot(time,acc_data['z'], '.', label='z')
#ax2.plot(time,smooth_z, 'k--', label='smooth z')
#plt.show()

#############################################################################
#
# ------------
#
# References
# """"""""""
#
# The use of the following functions, methods, classes and modules is shown
# in this example:
#
#import matplotlib
#matplotlib.axes.Axes.plot
#matplotlib.pyplot.plot
#matplotlib.axes.Axes.legend
#matplotlib.pyplot.legend