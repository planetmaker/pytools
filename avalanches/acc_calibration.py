#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 22:37:22 2019

@author: planetmaker
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dtc201902_data import drops, data_path, get_calibration
# from dtc201902_data import calibration as cal

(cal_filename, f_logging, t_z_plus, t_z_minus, t_y_plus, t_y_minus, t_x_plus, t_x_minus) = get_calibration()

def calibrate_axis(timeline, minus_start, minus_end, null_start, null_end, plus_start, plus_end):
    minus_vec = timeline[minus_start:minus_end]
    null_vec  = timeline[null_start:null_end]
    plus_vec  = timeline[plus_start:plus_end]

    minus = (np.mean(minus_vec), np.std(minus_vec))
    null  = (np.mean(null_vec), np.std(null_vec))
    plus  = (np.mean(plus_vec), np.std(plus_vec))

    return (minus, null, plus)

def suggest_calibration_axis(timeline, minus_start, minus_end, null_start, null_end, plus_start, plus_end):
    minnullplus = calibrate_axis(timeline, minus_start, minus_end, null_start, null_end, plus_start, plus_end)

    print(minnullplus[2][0]+minnullplus[0][0], minnullplus[1][0])

    return minnullplus


def read_sensor_file(filename):
    sensor_arr = pd.read_csv(filename, sep='\t', header=2, decimal=',', names=['x','y','z'])
    return sensor_arr

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth



print('Calibration data:')
cal_data = read_sensor_file(data_path + cal_filename)

print('x: ',calibrate_axis(cal_data['x'], t_x_minus[0], t_x_minus[1], t_z_plus[0],  t_z_plus[1],  t_x_plus[0], t_x_plus[1]))
print('y: ',calibrate_axis(cal_data['y'], t_y_minus[0], t_y_minus[1], t_z_plus[0],  t_z_plus[1],  t_y_plus[0], t_y_plus[1]))
print('z: ',calibrate_axis(cal_data['z'], t_z_minus[0], t_z_minus[1], t_y_minus[0], t_y_minus[1], t_z_plus[0], t_z_plus[1]))




# drop07
#acc_filename = '/home/planetmaker/Bilder/dtc_201902/drop07/acc_drop07.txt'
#t_pre_spin = [1500*f_logging,1575*f_logging]
#t_spin = [1600*f_logging,1675*f_logging]
#t_0g   = [1693*f_logging,1695*f_logging]

# drop08
#acc_filename = '/home/planetmaker/Bilder/dtc_201902/drop08/acc-data/drop08.txt'
#t_pre_spin = [1485*f_logging,1510*f_logging]
#t_spin = [1540*f_logging,1552*f_logging]
#t_0g   = [1557*f_logging,1559*f_logging]

# drop09
#acc_filename = '/home/planetmaker/Bilder/dtc_201902/drop09/acc-data/drop09.txt'
#t_pre_spin = [1720*f_logging,1820*f_logging]
#t_spin = [1840*f_logging,1880*f_logging]
#t_0g   = [1892*f_logging,1894*f_logging]

# drop10
#acc_filename = '/home/planetmaker/Bilder/dtc_201902/drop10/acc-data/drop10.txt'
#t_pre_spin = [1840*f_logging,1880*f_logging]
#t_spin = [1900*f_logging,1940*f_logging]
#t_0g   = [1951*f_logging,1954*f_logging]
#

for drop, values in drops.items():
    acc_filename = data_path + values.get('acc_filename')
    t_pre_spin = values.get('t_pre_spin')
    t_spin = values.get('t_spin')
    t_0g = values.get('t_0g')
    acc_data = read_sensor_file(acc_filename)
    time = [t/400 for t in range(0,len(acc_data['x']))]

    # Create plots with pre-defined labels.
    fig, ax = plt.subplots()
    plt.gcf().canvas.set_window_title(drop + 'acc-data')
    ax.plot(time, acc_data['x'], 'k--', label='x')
    ax.plot(time, acc_data['y'], 'b:', label='y')
    ax.plot(time, acc_data['z'], 'r', label='z')

    smooth_x = smooth(acc_data['x'],50)
    smooth_y = smooth(acc_data['y'],50)
    smooth_z = smooth(acc_data['z'],50)

    print('\n')
    print(drop)
    try:
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
    except TypeError:
        print('No value ranges defined!')
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