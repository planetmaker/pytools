#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 11:33:12 2019

@author: ingo
"""

from enum import Enum
data_path = '/home/ingo/icaps/eisige_lawinen/dtc2019/'

# Calibration measurement of the on-centrifuge acc sensor.
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

# Placement of extra weight for rotational stability
class CapsuleBalance(Enum):
    UNBALANCED = 1
    COUNTER_WEIGHT = 2
    FULLY_BALANCED = 3

# Placement of the on-centrifuge acc sensor
class AccPosition(Enum):
    ACC_POS_BEHIND = 1
    ACC_POS_IN_FRONT = 2

# Position of the experiment chamber from the centrifuge center
radius_inner  = 0.13  # meters
radius_middle = 0.155 # meters
radius_outer  = 0.18  # meters

# Material types flown
class Material(Enum):
    CRUSHED_25 = 1
    CRUSHED_16_25 = 2
    CRUSHED_10_16 = 3
    SPHERES_50 = 4

drops = {
        'drop01': {
                'temperature': -111,
                'material': Material.CRUSHED_25,
                'target_g': 0.3,
                'balance': CapsuleBalance.UNBALANCED,
                'rpm_video': 60/(1 * (954-120) / 500),
                'fps': 500,
                },
        'drop02': {
                'temperature': -130,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.3,
                'balance': CapsuleBalance.UNBALANCED,
                'fps': 500,
                },
        'drop03': {
                'temperature': -116,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.3,
                'balance': CapsuleBalance.UNBALANCED,
                'fps': 500,
                },
        'drop04': {
                'temperature': -132,
                'material': Material.SPHERES_50,
                'target_g': 0.3,
                'balance': CapsuleBalance.UNBALANCED,
                'fps': 500,
                'rpm_video': 60/(1 * (914-67) / 500),
                },
        'drop05': {
                'temperature': -120,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.1,
                'balance': CapsuleBalance.UNBALANCED,
                'fps': 500,
                'rpm_video': 60/(1 * (1406-161) / 500),
                },
        'drop06': {
                'temperature': -96,
                'material': Material.SPHERES_50,
                'target_g': 0.03,
                'balance': CapsuleBalance.UNBALANCED,
                'fps': 1000,
                'rpm_video': 60/(2 * (2580-371) / 1000),
                },
        'drop07': {
                'acc_filename': 'drop07/acc-data/acc_drop07.txt',
                'acc_position': AccPosition.ACC_POS_BEHIND,
                't_pre_spin': [1500*calibration.get('f_logging'),1575*calibration.get('f_logging')],
                't_spin': [1600*calibration.get('f_logging'),1675*calibration.get('f_logging')],
                't_0g': [1693*calibration.get('f_logging'),1695*calibration.get('f_logging')],
                'temperature': -147,
                'material': Material.SPHERES_50,
                'target_g': 0.01,
                'balance': CapsuleBalance.UNBALANCED,
                'rpm_video': 60/(4 * (2105-242) / 1000),
                },
        'drop08': {
                'acc_filename': 'drop08/acc-data/drop08.txt',
                'acc_position': AccPosition.ACC_POS_BEHIND,
                't_pre_spin': [1485*calibration.get('f_logging'),1510*calibration.get('f_logging')],
                't_spin': [1540*calibration.get('f_logging'),1552*calibration.get('f_logging')],
                't_0g': [1557*calibration.get('f_logging'),1559*calibration.get('f_logging')],
                'temperature': -141,
                'material': Material.SPHERES_50,
                'target_g': 0.1,
                'balance': CapsuleBalance.UNBALANCED,
                'rpm_video': 60/(1 * (2710-200) / 1000),
                },
        'drop09': {
                'acc_filename': 'drop09/acc-data/drop09.txt',
                'acc_position': AccPosition.ACC_POS_BEHIND,
                't_pre_spin': [1720*calibration.get('f_logging'),1820*calibration.get('f_logging')],
                't_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
                't_0g': [1892*calibration.get('f_logging'),1894*calibration.get('f_logging')],
                'temperature': -140,
                'material': Material.SPHERES_50,
                'target_g': 0.003,
                'balance': CapsuleBalance.COUNTER_WEIGHT,
                'rpm_video': 60/(2 * (3914-733) / 1000),
                },
        'drop10': {
                'acc_filename': 'drop10/acc-data/drop10.txt',
                'acc_position': AccPosition.ACC_POS_BEHIND,
                't_pre_spin': [1840*calibration.get('f_logging'),1880*calibration.get('f_logging')],
                't_spin': [1900*calibration.get('f_logging'),1940*calibration.get('f_logging')],
                't_0g': [1951*calibration.get('f_logging'),1954*calibration.get('f_logging')],
                'temperature': -126,
                'material': Material.SPHERES_50,
                'target_g': 0.001,
                'balance': CapsuleBalance.FULLY_BALANCED,
                'rpm_video': 60/(4 * (4903-20) / 1000),
                },
        'drop11': {
                'acc_filename': 'drop11/acc-data/drop11.txt',
                'acc_position': AccPosition.ACC_POS_BEHIND,
                't_pre_spin': [2550*calibration.get('f_logging'),2600*calibration.get('f_logging')],
                't_spin': [2620*calibration.get('f_logging'),2660*calibration.get('f_logging')],
                't_0g': [2663*calibration.get('f_logging'),2666*calibration.get('f_logging')],
                'temperature': -113,
                'material': Material.SPHERES_50,
                'target_g': 0.01,
                'balance': CapsuleBalance.FULLY_BALANCED,
                'rpm_video': 60/(4 * (2497-582) / 1000),
                },
        'drop12': {
                'acc_filename': 'drop12/acc-data/drop12.txt',
                'acc_position': AccPosition.ACC_POS_BEHIND,
                't_pre_spin': [1000*calibration.get('f_logging'),1900*calibration.get('f_logging')],
                't_spin': [2030*calibration.get('f_logging'),2050*calibration.get('f_logging')],
                't_0g': [2053*calibration.get('f_logging'),2056*calibration.get('f_logging')],
                'temperature': -124,
                'material': Material.CRUSHED_10_16,
                'target_g': 0.3,
                'balance': CapsuleBalance.FULLY_BALANCED,
                },
        'drop13': {
                'acc_filename': 'drop13/acc-data/drop13.txt',
                'acc_position': AccPosition.ACC_POS_BEHIND,
                't_pre_spin': [1000*calibration.get('f_logging'),1700*calibration.get('f_logging')],
                't_spin': [1875*calibration.get('f_logging'),1950*calibration.get('f_logging')],
                't_0g': [1954*calibration.get('f_logging'),1957*calibration.get('f_logging')],
                'temperature': -123,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.01,
                'balance': CapsuleBalance.FULLY_BALANCED,
                'rpm_video': 60/(4 * (1944-73) / 1000),
                },
        'drop14': {
                'acc_filename': 'drop14/acc-data/drop14.txt',
                'acc_position': AccPosition.ACC_POS_IN_FRONT,
                't_pre_spin': [1800*calibration.get('f_logging'),2200*calibration.get('f_logging')],
                't_spin': [2290*calibration.get('f_logging'),2365*calibration.get('f_logging')],
                't_0g': [2372*calibration.get('f_logging'),2375*calibration.get('f_logging')],
                'temperature': -115,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.001,
                'balance': CapsuleBalance.FULLY_BALANCED,
                # 'rpm_video': Not possible. Too slow rotation and only one stringer visible
                },
        'drop15': {
                'acc_filename': 'drop15/acc-data/drop15.txt',
                'acc_position': AccPosition.ACC_POS_IN_FRONT,
                't_pre_spin': [1400*calibration.get('f_logging'),1900*calibration.get('f_logging')],
                't_spin': [2040*calibration.get('f_logging'),2110*calibration.get('f_logging')],
                't_0g': [2117*calibration.get('f_logging'),2120*calibration.get('f_logging')],
                'temperature': -124,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.03,
                'balance': CapsuleBalance.FULLY_BALANCED,
                'rpm_video': 60/(4 * (1553-403) / 1000),
                },
        'drop16': {
                'acc_filename': 'drop16/acc-data/drop16.txt',
                'acc_position': AccPosition.ACC_POS_IN_FRONT,
                't_pre_spin': [2000*calibration.get('f_logging'),2400*calibration.get('f_logging')],
                't_spin': [2510*calibration.get('f_logging'),2540*calibration.get('f_logging')],
                't_0g': [2548*calibration.get('f_logging'),2551*calibration.get('f_logging')],
                'temperature': -115,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.03,
                'balance': CapsuleBalance.FULLY_BALANCED,
                'rpm_video': 60/(4 * (1624-479) / 1000),
                },
        'drop17': {
                'acc_filename': 'drop17/acc-data/drop17.txt',
                'acc_position': AccPosition.ACC_POS_IN_FRONT,
                't_pre_spin': [1700*calibration.get('f_logging'),2200*calibration.get('f_logging')],
                't_spin': [2260*calibration.get('f_logging'),2320*calibration.get('f_logging')],
                't_0g': [2329*calibration.get('f_logging'),2332*calibration.get('f_logging')],
                'temperature': -121,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.003,
                'balance': CapsuleBalance.FULLY_BALANCED,
                'rpm_video': 60/(4 * (3248-85) / 1000),
                },
        'drop18': {
                'acc_filename': 'drop18/acc-data/drop18.txt',
                'acc_position': AccPosition.ACC_POS_IN_FRONT,
                't_pre_spin': [2000*calibration.get('f_logging'),2400*calibration.get('f_logging')],
                't_spin': [2585*calibration.get('f_logging'),2615*calibration.get('f_logging')],
                't_0g': [2620*calibration.get('f_logging'),2623*calibration.get('f_logging')],
                'temperature': -116,
                'material': Material.CRUSHED_16_25,
                'target_g': 0.3,
                'balance': CapsuleBalance.UNBALANCED,
                },
        }

def get_calibration():
    return (calibration.get('acc_cal_filename'), calibration.get('f_logging'),
            calibration.get('t_z_plus'), calibration.get('t_z_minus'),
            calibration.get('t_y_plus'), calibration.get('t_y_minus'),
            calibration.get('t_x_plus'), calibration.get('t_x_minus'))
