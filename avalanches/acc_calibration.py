#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 22:37:22 2019

@author: planetmaker
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dtc201902_data as dtcdata
# from dtc201902_data import calibration as cal

(cal_filename, f_logging, t_z_plus, t_z_minus, t_y_plus, t_y_minus, t_x_plus, t_x_minus) = dtcdata.get_calibration()

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
    if box_pts == 1:
        return y

    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth



print('Calibration data:')
cal_data = read_sensor_file(dtcdata.data_path + cal_filename)

print('x: ',calibrate_axis(cal_data['x'], t_x_minus[0], t_x_minus[1], t_z_plus[0],  t_z_plus[1],  t_x_plus[0], t_x_plus[1]))
print('y: ',calibrate_axis(cal_data['y'], t_y_minus[0], t_y_minus[1], t_z_plus[0],  t_z_plus[1],  t_y_plus[0], t_y_plus[1]))
print('z: ',calibrate_axis(cal_data['z'], t_z_minus[0], t_z_minus[1], t_y_minus[0], t_y_minus[1], t_z_plus[0], t_z_plus[1]))

class dtc_acc_centrifuge():
    name = ""
    drop_data = {}
    sensor_data = None

    def __init__(self, name):
        self.name = name
        self.drop_data = dtcdata.drops.get(name)

    def read(self):
        try:
            acc_filename = dtcdata.data_path + self.drop_data.get('acc_filename')
        except TypeError:
            print("No on-centrifuge acceleration data available for {}".format(self.name))
        else:
            self.sensor_data = read_sensor_file(acc_filename)

    def get_axis(self, axis, smooth=1):
        if self.sensor_data is None:
            self.read()

        try:
            return self.sensor_data.get(axis)
        except AttributeError:
            print("No on-centrifuge acceleration data available for {}".format(self.name))

    def get_time(self):
        if self.sensor_data is None:
            self.read()

        try:
            return [t/self.sampling_rate for t in range(0, len(self.sensor_data['x']))]
        except AttributeError:
            print("No on-centrifuge acceleration data available for {}".format(self.name))
            return None

    def plot(self):
        if self.sensor_data is None:
            self.read()

        try:
            t_pre_spin = self.drop_data.get('t_pre_spin')
            t_spin = self.drop_data.get('t_spin')
            t_0g = self.drop_data.get('t_0g')
            time = [t/400 for t in range(0,len(self.sensor_data['x']))]
        except AttributeError:
            print("No on-centrifuge acceleration data available for {}".format(self.name))
            return

        # Create plots with pre-defined labels.
        fig, ax = plt.subplots()
        plt.gcf().canvas.set_window_title(self.name + ' acc-data')
        ax.plot(time, self.sensor_data['x'], 'k--', label='x')
        ax.plot(time, self.sensor_data['y'], 'b:', label='y')
        ax.plot(time, self.sensor_data['z'], 'r', label='z')

        smooth_x = smooth(self.sensor_data['x'],50)
        smooth_y = smooth(self.sensor_data['y'],50)
        smooth_z = smooth(self.sensor_data['z'],50)

        print('\n')
        print(self.name)
        try:
            print('Values for 1g:')
            prespin = self.sensor_data[:][t_pre_spin[0]:t_pre_spin[1]]
            print('x = {} +- {}'.format(np.mean(prespin['x']),np.std(prespin['x'])))
            print('y = {} +- {}'.format(np.mean(prespin['y']),np.std(prespin['y'])))
            print('z = {} +- {}'.format(np.mean(prespin['z']),np.std(prespin['z'])))

            print('Values for 1g with centrifuge:')
            spin = self.sensor_data[:][t_spin[0]:t_spin[1]]
            print('x = {} +- {} ({}..{})'.format(np.mean(spin['x']),np.std(spin['x']), np.min(smooth_x), np.max(smooth_x)))
            print('y = {} +- {} ({}..{})'.format(np.mean(spin['y']),np.std(spin['y']), np.min(smooth_y), np.max(smooth_y)))
            print('z = {} +- {} ({}..{})'.format(np.mean(spin['z']),np.std(spin['z']), np.min(smooth_z), np.max(smooth_z)))

            print('Values for 0g:')
            nullg = self.sensor_data[:][t_0g[0]:t_0g[1]]
            print('x = {} +- {}'.format(np.mean(nullg['x']),np.std(nullg['x'])))
            print('y = {} +- {}'.format(np.mean(nullg['y']),np.std(nullg['y'])))
            print('z = {} +- {}'.format(np.mean(nullg['z']),np.std(nullg['z'])))
        except TypeError:
            print('No value ranges defined!')
        legend = ax.legend(loc='upper left', shadow=False, fontsize='x-large')

        # Put a nicer background color on the legend.
        #legend.get_frame().set_facecolor('C0')

        plt.show()



def show_all_acc_centrifuge():
    for drop in dtcdata.drops:
        this_drop = dtc_acc_centrifuge(drop)
        this_drop.show()