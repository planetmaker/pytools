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

import dtc201902_data as dtcdata


def get_material(drops):
    pass


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


class dtc2019():
    def __init__(self):
        props = ['temperature', 'material', 'target_g', 'fps']
        self.dataset = pd.DataFrame()
        self.dataset['name'] = get_drop_names()
        # Get the easy properties which need no conversion
        for prop in props:
            self.dataset[prop] = get_drop_property(prop)
        self.dataset['manual_angle'], self.dataset['stddev manual_angle'] = get_manual_angle()

if __name__ == '__main__':
    pass
