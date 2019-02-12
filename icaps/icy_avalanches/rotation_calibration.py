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
    omega = r_values
    f = omega
    rpm = omega
    for i,r in enumerate(r_values):
        omega[i] = sqrt(a / (r / 100))
        f[i] = omega[i] / 2 / pi
        rpm[i] = f[i] * 60
    #print(g, ": ", omega)
    print("{}: {}".format(a/9.81,["{0:0.2f}".format(o) for o in rpm]))
    
# Convert the rpm values to voltage as by the centrifuge calibration data

