#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes and code related to analysis of acceleration sensor data
Created on Fri Sep 28 13:07:06 2018

@author: ingo
"""
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import savgol_filter
from scipy.ndimage.interpolation import shift

from ods_experiment_table import ods_experiment_table

from bne_config import bne_config
from cast_lists import list_to_float

"""
Class for analysing acceleration sensor data"
"""
class bne_acc_sensor_data:
    data = {
            'raw_accdata': None,
            'a': None,
            'smooth_a': None,
            't': None,
            'name': "",
            'frequency': np.NaN,
            'duration': np.NaN,

            'level0g': np.NaN,
            'level1g': np.NaN,
            'scaleg': np.NaN,
            'trigger_offset': np.NaN,

            'rising_flanks': [],
            'dropping_flanks': [],
            }

    def __init__(self, data = None, name = "", duration = 1.0):
        """
        Initialize the sensor data.

        @param data Optionally a list of 5000 datapoints with the data
        @param name Name of the data (e.g. the stage programme name)
        @param duration Duration in seconds covered by the data
        """
        if type(duration) is not float:
            duration = 1.0

        self.data['raw_accdata'] = data
        self.data['t'] = np.arange(0, duration, duration/5000, dtype=float)
        self.data['name'] = name
        self.data['duration'] = duration
        self.data['level0g'] = 2.4655959
        self.data['level1g'] = 2.4412975
        self.data['scaleg'] = self.data['level1g'] - self.data['level0g']
        self.data['trigger_offset'] = 0.00851714

    def read_from_file(self, filename):
        """
        Read sensor data from a file into the class's storage for raw_accdata

        The filename's path is provided from bne_config via the dict entries
        'project_path' and relative to that 'sensor_path'.

        @param filename Filename with complete path to read from.
        """
        with open(filename, 'r') as f:
            str_values = f.readlines()
        str_values = [s.replace("\n", "") for s in str_values]
        self.data['raw_accdata'] = (list_to_float(str_values, np.NaN, decimal_sep=',')[1:])[:-1]

    def raw_to_acc(self):
        """
        Convert the raw_accdata into actual acceleration data

        Kalibration data are read from this class' internal settings
        """
        assert(self.data.get('raw_accdata') is not None)
        self.data['a'] = [-(y - self.data['trigger_offset']) / self.data['scaleg'] for y in self.data['raw_accdata']]

    def get(self, prop):
        return self.data.get(prop)

    def get_a_t(self):
        """
        Return acceleration data and related time stamps in SI units

        @return acceleration in m/s^2
        @return time in s
        """
        return self.data.get('a'), self.data.get('t')

    def get_f(self):
        """
        Analyse the acceleration data to obtain a vibration frequency
        assuming 'full taps'

        @return frequency in Hz
        """
        if self.data.get('a') is None:
            self.raw_to_acc()
        smooth_a = savgol_filter(self.data.get('a'), 101, 3)
        gradient_a = np.gradient(smooth_a)

        mean_grad_a = np.mean(gradient_a)
        min_grad_a  = np.min(gradient_a)
        max_grad_a = np.max(gradient_a)
        amp_grad_a = (max_grad_a - min_grad_a) / 2

        mean_smooth_a = np.mean(smooth_a)
        min_smooth_a = np.min(smooth_a)
        max_smooth_a = np.max(smooth_a)
        amp_smooth_a = (max_smooth_a - min_smooth_a) / 2

        shift_smooth_a = shift(smooth_a, -25, cval=np.NaN)

        index_positive_grad_a = savgol_filter(gradient_a, 7, 3) > (0.5 * amp_grad_a + mean_grad_a)
        index_high_a = shift_smooth_a > (mean_smooth_a + 0.5* amp_smooth_a)

        peaks = index_high_a * index_positive_grad_a
        for index,g in enumerate(peaks):
            if g == True and peaks[index-1] != True:
                try:
                    self.data['rising_flanks'].append(self.data.get('t')[index])
                except:
                    print("{}: No time set.".format(self.data.get('name')))
                    self.data['frequency'] = np.NaN
                    return np.NaN

        self.data['frequency'] = np.NaN
        if len(self.data.get('rising_flanks')) == 2:
            dt = self.data.get('rising_flanks')[1] - self.data.get('rising_flanks')[0]
            self.data['frequency'] = 1 / dt
        else:
            print("{}: Several rising flanks with subsequent positive g found: ".format(self.data.get('name')))
            print(self.data.get('rising_flanks'))

        self.data['smooth_a'] = smooth_a
        return self.data.get('frequency')


    def plot(self):
        fig, ax = plt.subplots(num='Sensor data for {}'.format(self.data.get('name')))
        plt.xlabel('time [s]')
        plt.ylabel('acceleration [g]')
        ax.plot(self.data.get('t'), self.data.get('a'), '+', label='a')
        ax.plot(self.data.get('t'), self.data.get('smooth_a'), label='smoothed a')
        ylim = plt.ylim()
        plt.autoscale(False)
        for t in self.data.get('rising_flanks'):
            plt.plot([t,t],[ylim[0],ylim[1]], color='black', linewidth=3)
        plt.autoscale(True)
        legend = ax.legend(loc='lower right')
        plt.show()

class get_stage_programmes(ods_experiment_table):

    def __init__(self, filename: str, sheetname: str):
        translate_dict = {
                'ambient g': {
                        'new_header': 'ambient_g',
                        'type':       'float',
                        'conversion': 1.0,
                    },
                'excitation g': {
                        'new_header': 'rel_excitation',
                        'type':       'float',
                        'conversion': 1.0
                    },
                'Programme name': {
                        'new_header': 'prg_name',
                    },
                'Filename': {
                        'new_header': 'filename_pattern',
                    },
                'Plot-Duration [s]': {'new_header': 'str_duration',},
                'container': {'new_header': 'unused_container',},
            }

        super().__init__(filename, sheetname, translate_dict, True)
        self.decimal_sep = ','

    def read(self):
        super().read()

    def translate(self):
        super().translate()

        # ignore the question marks in the duration and assume that they are unfounded
        sd = []
        for d in self.data.get('str_duration'):
            if type(d) is str:
                d = d.replace("?", "")
                d = d.replace(",", ".")
            sd.append(d)
        self.data['duration'] = pd.to_numeric(sd, errors='coerce')

        self.data['sensordata'] = []
        for pattern,prg_name,duration in zip(self.data.get('filename_pattern'),self.data.get('prg_name'),self.data.get('duration')):
            filenames = glob.glob(bne_config.get('project_path') + bne_config.get('sensor_path') + pattern)
            if len(filenames) == 0:
                self.data['sensordata'].append(None)
                continue
            filename = filenames[0]

            print("{}: {}".format(prg_name,duration))
            sensordata = bne_acc_sensor_data(None, prg_name, duration)
            sensordata.read_from_file(filename)
            sensordata.raw_to_acc()
            sensordata.get_f()
            sensordata.plot()

            self.data.update(sensordata.data)





