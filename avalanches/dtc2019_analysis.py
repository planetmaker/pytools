#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 13:56:08 2019

@author: Ingo von Borstel
@license: GPL v2+
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from enum import Enum

class AngleType(Enum):
    MANUAL = 1

import dtc201902_data as dtcdata
from dtc201902_data import Material

def get_drop_names():
    arr = []
    for item in dtcdata.drops:
        arr.append(item)
    return arr

def get_drop_property(property_name):
    arr = []
    for item,value in dtcdata.drops.items():
        arr.append(value.get(property_name))
    return arr

def get_manual_angle():
    arr = []
    stdarr = []
    for item, value in dtcdata.drops.items():
        tuple_arr = value.get('manual_90angle')
        val_arr = []
        # Get the measured angle for each image (and ignore the image number)
        try:
            for tup_item in tuple_arr:
                # print(tup_item)
                for angle in tup_item[1]:
                    val_arr.append(angle)
            # get mean measured angle and standard deviation
            val = np.mean(val_arr)
            std = np.std(val_arr)
            # Catch any error, though there shouldn't be any...
            try:
                arr.append(90 - val)
                stdarr.append(std)
            except TypeError:
                arr.append(np.NaN)
                stdarr.append(np.NaN)
        except TypeError:
            arr.append(np.NaN)
            stdarr.append(np.NaN)
    return arr, stdarr

def convert_imagecount_to_seconds(num_images, fps):
    try:
        duration = num_images / fps
    except:
        duration = np.NaN
    return duration

def get_avalanch_duration():
    arr_duration_min = []
    arr_reliable_min = []
    arr_duration_max = []
    arr_reliable_max = []
    for drop, data in dtcdata.drops.items():
        duration_min = np.NaN
        duration_max = np.NaN
        is_reliable_min = False
        is_reliable_max = False
        try:
            [av_start_img, drop_end_img] = data.get('observation_images')
            stop_start = data.get('avalanch_stop_image_start')
            stop_end   = data.get('avalanch_stop_image_end')

            count_min = np.mean(stop_start.get('imageno')) - av_start_img
            count_max = np.mean(stop_end.get('imageno')) - av_start_img
            is_reliable_min = not (stop_start.get('is_lower_bound'))
            is_reliable_max = not (stop_end.get('is_lower_bound'))
            duration_min = convert_imagecount_to_seconds(count_min, data.get('fps'))
            duration_max = convert_imagecount_to_seconds(count_max, data.get('fps'))
        except (TypeError, KeyError, AttributeError):
            print("No avalanch duration for {}".format(drop))

        arr_duration_min.append(duration_min)
        arr_duration_max.append(duration_max)
        arr_reliable_min.append(is_reliable_min)
        arr_reliable_max.append(is_reliable_max)

    return arr_duration_min, arr_duration_max, arr_reliable_min, arr_reliable_max


def get_angle(method = AngleType.MANUAL):
    if method == AngleType.MANUAL:
        return get_manual_angle()
    return get_manual_angle()


class dtc2019():
    def __init__(self, dataset = None):
        # First copy those properties which need not special treatment
        if dataset is not None:
            self.dataset = dataset
            return

        copy_props = ['temperature', 'material', 'target_g', 'fps', 'balance']
        self.dataset = pd.DataFrame()
        self.dataset['name'] = get_drop_names()
        # Get the easy properties which need no conversion
        for prop in copy_props:
            self.dataset[prop] = get_drop_property(prop)
        # retrieve the angle and mirror it on 90° to obtain the true angle of repose
        self.dataset['manual_angle'], self.dataset['stddev manual_angle'] = get_manual_angle()
        # get the avalanch durations
        self.dataset['duration_min'], self.dataset['duration_max'], self.dataset['duration_min_reliability'], self.dataset['duration_max_reliability'] = get_avalanch_duration()

    def set_filter(self, filter_arr, filter_name = "unknown"):
        try:
            if filter_name == 'unknown':
                print("Using default filter name {}.".format(filter_name))
            self.dataset[filter_name] = filter_arr
        except ValueError as e:
            print("Mismatch between filter and data: {}".format(e))

    def get_filtered(self, filter_name = 'unknown'):
        try:
            ret = self.dataset[self.dataset[filter_name] == True]
        except KeyError:
            print("Filtering failed, filter not found: {}. Returning whole array.".format(filter_name))
            ret = self.dataset
        return ret

    def filtered_eq(self, filter_name, value):
        try:
            ret = self.dataset[self.dataset[filter_name] == value]
        except KeyError:
            print("Filtering failed, filter not found: {}. Returning whole array.".format(filter_name))
            ret = self.dataset
        return dtc2019(dataset = ret)

    def filtered_range(self, filter_name, vmin, vmax):
        try:
            ret = self.dataset[(self.dataset[filter_name] <= vmax) & (self.dataset[filter_name] >= vmin)]
        except KeyError:
            print("Filtering failed, filter not found: {}. Returning whole array.".format(filter_name))
            ret = self.dataset
        return dtc2019(dataset = ret)

    def plot(self, x, y, fig = None, ax = None, symbol = None, **kwargs):
        if fig is None:
            fig, ax = plt.subplots()
            plt.gcf().canvas.set_window_title("{} vs. {}".format(y,x))
        if symbol is None:
            symbol = 'k+'
        print(symbol)
        ax.plot(self.dataset[x], self.dataset[y], symbol, label=y, **kwargs)
        return fig, ax

    def errorplot(self, x, y, fig = None, ax = None, symbol = None, **kwargs):
        if fig is None:
            fig, ax = plt.subplots()
            plt.gcf().canvas.set_window_title("{} vs. {}".format(y,x))
        if symbol is None:
            symbol = 'k+'
        indices = np.argsort(self.dataset[x])
        xv = self.dataset[x][indices]
        yv = self.dataset[y][indices]
        ax.errorbar(xv, yv, yerr=0.1)
        return fig, ax

if __name__ == '__main__':
    dtc = dtc2019()
    # dtc.filtered('material','Material.CRUSHED_16_25').plot('target_g','manual_angle')
    pass
