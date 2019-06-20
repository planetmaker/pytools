#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""@package single_stage_programme
Created on Fri Aug 10 11:22:32 2018

@author: ingo
"""

import warnings

from tools.ODSReader import ODSReader

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.ndimage.interpolation import shift

import matplotlib.pyplot as plt

from BNE.bne_config import bne_config
from tools.cast_lists import cast_to_float, list_to_int

default_calibration = {
        'level0g': 2.4655959,
        'level1g': 2.4412975,
        'trigger_offset': 0.00851714,
        }

programme_table_filename = bne_config.get('project_path') + bne_config.get('filename_stage_programmes')
sensor_file_path = bne_config.get('project_path') + bne_config.get('sensor_path')

calibration_keys = ['level0g', 'level1g', 'trigger_offset']


def find_nearest(array,value):
    """Find the nearest list entry for a given value

    @param array The array to search in
    @param value The value to find the nearest list entry for
    """
    idx = (np.abs(array-value)).argmin()
    return array[idx]

def get_key(dictionary, key, default = None):
    """ Return the value of a key from a dict

    When the key is not found in the dict, then return None

    @param dictionary A dictionary to search through
    @param key        The key to look for in the dictionary
    @return value of the key, if found, otherwise None

    """
    try:
        return dictionary.get(key, default)
    except AttributeError:
        return default


class stage_programme_names:
    filename = programme_table_filename
    programmes = None
    programme_info = None

    def __init__(self, filename = programme_table_filename):
        self.filename = filename

    def read_file(self):
        assert (self.filename is not None), "No filename to read specified"
        doc = ODSReader(self.filename, clonespannedcolumns = True)
        self.programmes = doc.getSheet(bne_config.get('sheetname_stage_programmes'))

    def __str__(self):
        s = "Stage programmes read from {}\n".format(self.filename)
        if self.programmes is not None:
            for line in self.programmes:
                try:
                    duration = line[8]
                except:
                    duration = None
                s += "{}: {}g x {}. Duration: {}; Prg: {}\n".format(line[3],line[0],line[1],duration,line[4])
        return s

    def get_programme_info(self):
        retval = {
                'ambient_g': [],
                'relative_excitation': [],
                'name': [],
                'filenames': [],
                'acc_rise_times': [],
                'duration': []
                }
        for line in self.programmes:
            retval['ambient_g'].append(line[0])
            retval['name'].append(line[3])
            retval['relative_excitation'].append(line[1])
            retval['filenames'].append(line[4])
            retval['acc_rise_times'].append([line[6],line[7]])
            try:
                duration = line[8]
            except:
                duration = None
            retval['duration'].append(duration)

        self.programme_info = retval
        return retval

    def get_by_name(self, search_name):
        if search_name is None:
            print("We need a name or cannot return anything!")
            return None

        assert (search_name is not None), "No name specified"

        index = [i for i, name in enumerate(self.programme_info['name']) if name == search_name]
        ret_dict = self.programm_info
        for key in self.programme_info:
            ret_dict[key] = self.programme_info[key][index]
        return ret_dict


    def get_programmes(self):
        return self.programmes

    def get_programmes_as_dict(self):
        retval = {}
        for name, rel_exc, ambient_g, filenames, acc_rise, duration in zip(self.programme_info.get('name'), self.programme_info.get('relative_excitation'), self.programme_info.get('ambient_g'), self.programme_info.get('filenames'), self.programme_info.get('acc_rise_times'), self.programme_info.get('duration')):
            if duration is not None:
                duration = duration.replace('?','')
            retval[name] = {
                    'rel_excitation': cast_to_float(rel_exc, np.NaN, decimal_sep=','),
                    'ambient_g': cast_to_float(ambient_g, np.NaN, decimal_sep=','),
                    'acc_rise_times': list_to_int(acc_rise, np.NaN),
                    'duration': cast_to_float(duration, np.NaN, decimal_sep=','),
                    'filename_pattern': filenames,
                  }
        return retval


class single_stage_programme:
    """
    Class to contain the data for a stage programme, including the intended
    acceleration and excitation as well as the overall curve
    """
    name = None
    filename = None
    g = None
    excitation = None
    raw_acc_data = None
    calibration = default_calibration
    frequency = None
    shaking_duration = None
    length_in_seconds = None
    acc_analysis = {}
    acc_data = {}
    cid = None

    def __init__(self, name = None, filename = None, path = sensor_file_path):
        self.name = name
        self.filename = filename
        self.path = path
        self.ambient_g = None
        self.relative_excitation = None
        self.raw_acc_data = []
        self.length_in_seconds = None
        self.shaking_duration = None

        self.calibration = default_calibration
        self.calibration['scaleg'] = self.calibration['level1g'] - self.calibration['level0g']

        self.acc_analysis = {}
        self.acc_data = {}

    def __repr__(self):
        return "<single_stage_programme: '{}' from '{}' with {} datapoints".format(self.name, self.filename, len(self.raw_acc_data))

    def __str__(self):
        s  = "single_stage_programme: '{}' from '{}': {}g x {}".format(self.name, self.filename, self.ambient_g, self.relative_excitation)
        s += "\n    {} datapoints in {} seconds (f={}Hz)".format(len(self.raw_acc_data), self.length_in_seconds, self.frequency)
        try:
            s += "\n    rise times: " + ", ".join( map(str, self.acc_analysis.get('peak_times')))
        except:
            s += "\n    rise times: None"

        return s

    def set_calibration(self, calibration):
        assert (type(calibration) == dict), "calibration needs to be a dict with keys 'level0g', 'level1g' and 'trigger_offset'. Optionally also 'scaleg'."
        for key in calibration_keys:
            assert (key in calibration), "key '{}' not found in supplied dict.".format(key)
        self.calibration = calibration
        if not 'scaleg' in calibration:
            self.calibration['scaleg'] = self.calibration['level1g'] - self.calibration['level0g']

    def read_by_filename(self, filename=None, length_in_seconds=None):
        """
        Read the stage acceleration data from a filename

        @param filename: Filename to read the acceleration data from
        @type  fname: C{str}
        """
        if filename is None and self.filename is None:
            print("No filename given, but we need a file to read from.")
            return
        elif filename is not None:
            self.filename = filename

        assert (self.filename is not None), "We need a filename to read."
        with open(self.filename, 'r') as f:
            str_values = f.readlines()

        str_values = [s.replace("\n", "") for s in str_values]
        str_values = [s.replace(",", ".") for s in str_values]

        num_strings = len(str_values)
        self.raw_acc_data = [float(s) for s in str_values[1:num_strings-1]]
        if length_in_seconds is not None:
            self.length_in_seconds = length_in_seconds

    def extract_data(self, data = None, length_in_seconds = None, acc_rise_times = None):
        if data is None:
            data = self.raw_acc_data
        else:
            self.raw_acc_data = data
        assert (type(data) == list), "The acceleration measurements need to be a list! It is {}".format(type(data))
        assert (len(data) > 0), "The acceleration data contain 0 data points. No way to extract meaningful data from that"
        if length_in_seconds is None or np.isnan(length_in_seconds):
            length_in_seconds = self.length_in_seconds
        else:
            self.length_in_seconds = length_in_seconds

        if (length_in_seconds is None or np.isnan(length_in_seconds)):
            print("{}: We need to know the time base for the measurements! Nothing extracted.".format(self.name))
            return

        n_data = len(data)
        dt = length_in_seconds / n_data
        t = np.arange(0, n_data*dt, 1*dt, dtype=float)

        # print("{}: t={}s ({} points, {} rise times)".format(self.name, length_in_seconds, n_data, len(acc_rise_times)))

        real_acc = [-(datapoint - self.calibration['level0g']) / self.calibration['scaleg'] for datapoint in data]

        smooth_acc = savgol_filter(real_acc, 101, 3)
        gradient_acc = np.gradient(smooth_acc)
        mean_gradient_acc = np.mean(gradient_acc)
        min_gradient_acc = np.min(gradient_acc)
        max_gradient_acc = np.max(gradient_acc)
        amp_gradient_acc = (max_gradient_acc - min_gradient_acc) / 2

        mean_smooth_acc = np.mean(smooth_acc)
        min_smooth_acc = np.min(smooth_acc)
        max_smooth_acc = np.max(smooth_acc)
        amp_smooth_acc = (max_smooth_acc - min_smooth_acc) / 2

        shift_smooth_acc = shift(smooth_acc, -25, cval=np.NaN)

        t_gradient_acc_positive = savgol_filter(gradient_acc, 7, 3) > (0.5 * amp_gradient_acc + mean_gradient_acc)
        with np.warnings.catch_warnings():
            np.warnings.filterwarnings('ignore', r'invalid value')
            t_high_acc = shift_smooth_acc > (mean_smooth_acc + amp_smooth_acc * 0.5)

        if acc_rise_times is None:
            peak_times = []
            peaks = t_gradient_acc_positive * t_high_acc
            for time,g in enumerate(peaks):
                if g == True and peaks[time-1] != True:
                    peak_times.append(time)
            # print("Found rising flanks for positive g at: ", *peak_times)
        else:
            # peak_times = [time * dt for time in acc_rise_times]
            peak_times = acc_rise_times
            # print("Using supplied peak times: ", *peak_times)

        if len(peak_times) == 2 and all(np.isfinite(peak_times)):
            delta_t = t[peak_times[1]] - t[peak_times[0]]
            f = 1 / delta_t
            # print("Period = {:f}s and frequency = {:f}Hz.".format(delta_t, f))
        else:
            # print("More than 2 times found... that's bad!")
            delta_t = None
            f = None

        self.frequency = f
        self.shaking_duration = delta_t

        self.acc_analysis = {}
        self.acc_analysis['frequency'] = f
        self.acc_analysis['shaking_duration'] = delta_t
        self.acc_analysis['peak_times'] = peak_times
        self.acc_analysis['time'] = t

        self.acc_data = {}
        self.acc_data['smooth'] = {
                'acc': smooth_acc,
                'mean': mean_smooth_acc,
                'min': min_smooth_acc,
                'max': max_smooth_acc,
                'amplitude': amp_smooth_acc
                }
        self.acc_data['gradient'] = {
                'acc': gradient_acc,
                'mean': mean_gradient_acc,
                'min': min_gradient_acc,
                'max': max_gradient_acc,
                'amplitude': amp_gradient_acc
                }
        self.acc_data['shift_smooth'] = {
                'acc': shift_smooth_acc,
                'shift': -25
                }
        self.acc_data['real'] = {
                'acc': real_acc
                }

    def show_data(self, figure_no = None):

        if self.acc_analysis is None:
            self.extract_data()
        if not 'time' in self.acc_analysis or not 'gradient' in self.acc_data:
            print("{}: Nothing can be plotted. I'm still missing data. Run 'extract_data' first.".format(self.name))
            return

        if 'time' in self.acc_analysis:
            t = self.acc_analysis['time']
            xlabel = 'time [s]'
        else:
            xlabel = 'time [au]'

        if figure_no is None:
            if self.name is not None:
                figure_no = self.name
            else:
                figure_no = 'Acc data'
        if plt.fignum_exists(figure_no):
            plt.gcf().clear()
        else:
            plt.figure(figure_no)

        plt.plot(t, self.acc_data['real']['acc'])
        plt.xlabel(xlabel)
        plt.ylabel('acceleration [g]')
        if self.name is not None:
            plt.title = self.name

        if 'smooth' in self.acc_data:
            plt.plot(t, self.acc_data['smooth']['acc'])
        if 'peak_times' in self.acc_analysis and all(np.isfinite(self.acc_analysis.get('peak_times'))):
            ylim = plt.ylim()
            plt.autoscale(False)
            for time in self.acc_analysis['peak_times']:
                plt.plot([t[time],t[time]],[ylim[0],ylim[1]],color='black',linewidth=3)
            plt.autoscale(True)

        plt.show()


    def onclick(self, event):
        global ix, iy
        ix, iy = event.xdata, event.ydata
        print("{} / {}".format(event.xdata, event.ydata))

        global coords
        coords.append((ix, iy))


        fig = plt.figure(self.name)
        if len(coords) == 2:
            fig.canvas.mpl_disconnect(self.cid)
            plt.close(1)
        return

    def get_gamma(self):
        return self.excitation

    def get_shaking(self):
        # S = (Amplitude * omega)^2 / gh
        return ( (self.frequency * 2 * np.pi)**2 ) / (self.g * self.excitation * bne_config['g'] * bne_config['fill_height_ingo'])

    def get_duration_by_click(self):
        self.extract_data()
        fig = plt.figure(self.name)
        self.show_data()
        coords = []

        self.cid = fig.canvas.mpl_connect('button_press_event', self.onclick)

#        peak_times = []
        if self.acc_analysis is not None:
            time = self.acc_analysis.get('time', None)
        peak_times = []
        peak_times.append(np.where(time == (find_nearest(time, coords[0][0]))))
        peak_times.append(np.where(time == (find_nearest(time, coords[1][0]))))
        plt.show()

#        self.acc_analysis['peak_times'] = peak_times


    def get_frequency(self):
        if self.frequency is None:
            warnings.warn("Query for frequency, yet no frequency is yet determined")
            if 'frequency' in self.acc_analysis:
                self.frequency = self.acc_analysis['frequency']
        return self.frequency

