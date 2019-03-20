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
                print(tup_item)
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

def get_angle(method = AngleType.MANUAL):
    if method == AngleType.MANUAL:
        return get_manual_angle()
    return get_manual_angle()


class dtc2019():
    def __init__(self):
        # First copy those properties which need not special treatment
        copy_props = ['temperature', 'material', 'target_g', 'fps', 'balance']
        self.dataset = pd.DataFrame()
        self.dataset['name'] = get_drop_names()
        # Get the easy properties which need no conversion
        for prop in copy_props:
            self.dataset[prop] = get_drop_property(prop)
        # retrieve the angle and mirror it on 90° to obtain the true angle of repose
        self.dataset['manual_angle'], self.dataset['stddev manual_angle'] = get_manual_angle()

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

    def plot(self, x, y, **kwargs):
        fig, ax = plt.subplots()
        plt.gcf().canvas.set_window_title("{} vs. {}".format(y,x))
        ax.plot(self.dataset[x], self.dataset[y], 'k+', label=y, **kwargs)

if __name__ == '__main__':
    pass
