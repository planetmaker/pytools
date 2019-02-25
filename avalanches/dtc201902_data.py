#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 11:33:12 2019

@author: ingo
"""

data_path = '/home/ingo/icaps/eisige_lawinen/dtc2019/'

calibration = {
        'acc_cal_filename': 'acc_calibration_20190218.txt',
        'f_logging': 400,
        't_z_plus': [0*400, 10*400],
        't_z_minus': [21*400, 27*400],
        't_y_plus': [40*400, 55*400],
        't_y_minus': [64*400, 72*400],
        't_x_plus': [77*400, 83*400],
        't_x_minus': [89*400, 95*400],
        }

drops = {
        'drop07': {
                'acc_filename': 'drop07/acc-data/acc_drop07.txt',
                't_pre_spin': [1500*calibration.get('f_logging'),1575*calibration.get('f_logging')],
                't_spin': [1600*calibration.get('f_logging'),1675*calibration.get('f_logging')],
                't_0g': [1693*calibration.get('f_logging'),1695*calibration.get('f_logging')],
                },
        'drop08': {
                'acc_filename': 'drop08/acc-data/drop08.txt',
                't_pre_spin': [1485*calibration.get('f_logging'),1510*calibration.get('f_logging')],
                't_spin': [1540*calibration.get('f_logging'),1552*calibration.get('f_logging')],
                't_0g': [1557*calibration.get('f_logging'),1559*calibration.get('f_logging')],
                },
        'drop09': {
                'acc_filename': 'drop09/acc-data/drop09.txt',
                't_pre_spin': [1720*calibration.get('f_logging'),1820*calibration.get('f_logging')],
                't_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
                't_0g': [1892*calibration.get('f_logging'),1894*calibration.get('f_logging')],
                },
        'drop10': {
                'acc_filename': 'drop10/acc-data/drop10.txt',
                't_pre_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
                't_spin': [1900*calibration.get('f_logging'),1940*calibration.get('f_logging')],
                't_0g': [1951*calibration.get('f_logging'),1954*calibration.get('f_logging')],
                },
        'drop11': {
                'acc_filename': 'drop11/acc-data/drop11.txt',
                't_pre_spin': [2550*calibration.get('f_logging'),2600*calibration.get('f_logging')],
                't_spin': [2610*calibration.get('f_logging'),2660*calibration.get('f_logging')],
                't_0g': [2663*calibration.get('f_logging'),2666*calibration.get('f_logging')],
                },
#        'drop12': {
#                'acc_filename': 'drop12/acc-data/drop12.txt',
#                't_pre_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
#                't_spin': [1900*calibration.get('f_logging'),1940*calibration.get('f_logging')],
#                't_0g': [1951*calibration.get('f_logging'),1954*calibration.get('f_logging')],
#                },
#        'drop13': {
#                'acc_filename': 'drop13/acc-data/drop13.txt',
#                't_pre_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
#                't_spin': [1900*calibration.get('f_logging'),1940*calibration.get('f_logging')],
#                't_0g': [1951*calibration.get('f_logging'),1954*calibration.get('f_logging')],
#                },
#        'drop14': {
#                'acc_filename': 'drop14/acc-data/drop14.txt',
#                't_pre_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
#                't_spin': [1900*calibration.get('f_logging'),1940*calibration.get('f_logging')],
#                't_0g': [1951*calibration.get('f_logging'),1954*calibration.get('f_logging')],
#                },
#        'drop15': {
#                'acc_filename': 'drop15/acc-data/drop15.txt',
#                't_pre_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
#                't_spin': [1900*calibration.get('f_logging'),1940*calibration.get('f_logging')],
#                't_0g': [1951*calibration.get('f_logging'),1954*calibration.get('f_logging')],
#                },
#        'drop16': {
#                'acc_filename': 'drop16/acc-data/drop16.txt',
#                't_pre_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
#                't_spin': [1900*calibration.get('f_logging'),1940*calibration.get('f_logging')],
#                't_0g': [1951*calibration.get('f_logging'),1954*calibration.get('f_logging')],
#                },
#        'drop17': {
#                'acc_filename': 'drop17/acc-data/drop17.txt',
#                't_pre_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
#                't_spin': [1900*calibration.get('f_logging'),1940*calibration.get('f_logging')],
#                't_0g': [1951*calibration.get('f_logging'),1954*calibration.get('f_logging')],
#                },
        }

def get_calibration():
    return (calibration.get('acc_cal_filename'), calibration.get('f_logging'),
            calibration.get('t_z_plus'), calibration.get('t_z_minus'),
            calibration.get('t_y_plus'), calibration.get('t_y_minus'),
            calibration.get('t_x_plus'), calibration.get('t_x_minus'))
