#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 14:39:31 2019

@author: planetmaker
"""

from math import sqrt
from math import pi

r_inner = 13
r_outer = 18+1

r_step = 1

g_levels = [0.3, 0.1, 0.03, 0.01, 0.003, 0.001]
a_values = [9.81 * g for g in g_levels]

r_values = list(range(r_inner, r_outer))
print(r_values)

# a = omega^2 r
# Calculate omega for all relevant radii and g levels. Output it as table
print("g: [rpm (13cm), rpm (14cm),..., rpm (18cm)]")
for a in a_values:
    omega = r_values.copy()
    f = omega.copy()
    rpm = omega.copy()
    for i,r in enumerate(r_values):
        omega[i] = sqrt(a / (r / 100))
        f[i] = omega[i] / 2 / pi
        rpm[i] = f[i] * 60
    #print(g, ": ", omega)
    print("{}: {}".format(a/9.81,["{0:0.2f}".format(o) for o in rpm]))
    
# Convert the rpm values to voltage as by the centrifuge calibration data


# Übersetzung 60:40, Kalibrationskurve:
# rpm = -2.10924 + 9.9258 * U

def u_for_rpm(rpm):
    u = (rpm + 2.10924) / 9.9258
    return u


needed_rpm = {0.3: 42, 0.1: 24, 0.03: 13, 0.01: 7.5, 0.003: 4.2, 0.001: 2.4}
data_set = dict()
for item, value in needed_rpm.items():
    data_set[item] = {'rpm': value}
    data_set[item]['U'] = u_for_rpm(value)
    
print(data_set)

    