#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read and plot acceleration sensor data as obtained from the Agilent
oszilloscope, e.g. used in the BNE experiments

Created on Mon Aug  6 12:21:24 2018

@author: ingo
"""

import numpy as np
import matplotlib.pyplot as plt

# piece-wise, polynomial smoothing as suggested by
# https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way/20619164
# https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
# Savitzky, A.; Golay, M.J.E. (1964). "Smoothing and Differentiation of Data by Simplified Least Squares Procedures". Analytical Chemistry. 36 (8): 1627–39.
from scipy.signal import savgol_filter

from scipy.ndimage.interpolation import shift

from os.path import expanduser
PROJECT_PATH = expanduser("~") + "/icaps/BNE/"

file_path = PROJECT_PATH + "/sensor/"
# file_name = "Waveform2.00g-fulltaps_ch1_130ff_nut8mm_007.txt"

# filenames =

dt = 1/5000
da = 1

with open(file_path + file_name, 'r') as f:
    str_values = f.readlines()

#for i,s in enumerate(str_values):
#    s = s.replace("\n","")              # remove the trailing new line char
#    str_values[i] = s.replace(",",".")  # make numbers readable
str_values = [s.replace("\n", "") for s in str_values]
str_values = [s.replace(",", ".") for s in str_values]


num_strings = len(str_values)
#values = list(map(float, str_values[1:num_strings-1]))
values = [float(s) for s in str_values[1:num_strings-1]]


t = np.arange(0, 5000*dt, 1*dt, dtype=float)

level0g = 2.4655959
level1g = 2.4412975
scaleg = level1g - level0g
trigger_offset = 0.00851714

#a = values
#for i,y in enumerate(a):
#    a[i] = (y - trigger_offset) * scaleg
a = [-(y - trigger_offset) / scaleg for y in values]

plt.figure(1)
plt.gcf().clear()
plt.plot(t, a)
plt.show()

smooth_a = savgol_filter(a, 101, 3)
plt.plot(t, smooth_a)
plt.show()

plt.figure(2)
plt.gcf().clear()
gradient_a = np.gradient(smooth_a)
plt.plot(gradient_a)
plt.show()

mean_gradient_a = np.mean(gradient_a)
min_gradient_a = np.min(gradient_a)
max_gradient_a = np.max(gradient_a)
amp_gradient_a = (max_gradient_a - min_gradient_a) / 2

mean_smooth_a = np.mean(smooth_a)
min_smooth_a = np.min(smooth_a)
max_smooth_a = np.max(smooth_a)
amp_smooth_a = (max_smooth_a - min_smooth_a) / 2

# shift the acceleration values a bit to earlier times in order to compare
# them with the gradient, so that we get the matches we want.
shift_smooth_a = shift(smooth_a, -25, cval=np.NaN)

t_gradient_a_positive = savgol_filter(gradient_a,7,3) > (0.5 * amp_gradient_a + mean_gradient_a)
t_high_a = shift_smooth_a > (mean_smooth_a + amp_smooth_a * 0.5)

plt.figure(3)
plt.gcf().clear()
plt.plot(t_gradient_a_positive * t_high_a)
plt.show()

times = []
peaks = t_gradient_a_positive * t_high_a
for time,g in enumerate(peaks):
    if g == True and peaks[time-1] != True:
        print("Found rising flank for positive g at {}".format(time))
        times.append(time)

plt.figure(1)
ylim = plt.ylim()
plt.autoscale(False)
for time in times:
    plt.plot([t[time],t[time]],[plt.ylim()[0],plt.ylim()[1]],color='black',linewidth=3)
plt.autoscale(True)

if len(times) != 2:
    print("More than 2 times found... that's bad!")
    dt = np.NaN
    f = np.NaN
else:
    dt = t[times[1]] - t[times[0]]
    f = 1 / dt
    print("Period = {:f}s and frequency = {:f}".format(dt, f))

