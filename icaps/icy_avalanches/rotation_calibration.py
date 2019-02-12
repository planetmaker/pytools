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

r_values = list(range(r_inner, r_outer))
print(r_values)

# a = omega^2 r

for g in g_levels:
    omega = r_values
    f = omega
    rpm = omega
    for i,r in enumerate(r_values):
        omega[i] = sqrt(g / r * 100)
        f[i] = omega[i] / 2 / pi
        rpm[i] = f[i] * 60
    #print(g, ": ", omega)
    print("{}: {}".format(g,["{0:0.2f}".format(o) for o in rpm]))