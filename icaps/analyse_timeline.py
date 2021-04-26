#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Might need python >= 3.8 or related matplotlib
"""
Created on Tue Apr 21 14:45:51 2020

@author: planetmaker
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

filename_housekeeping = "~/PowerFolders/ICAPS_data_analysis/Housekeeping/log_1000Hz_15112019_113621.csv"
filename_timeline     = "~/PowerFolders/ICAPS_data_analysis/ICAPS_event_timeline_20200423.xlsx"

df = pd.read_csv(filename_housekeeping, sep=';') # , index_col='time_stamp')

#print(df['oos2'])

# Count how many triggers are sent to the OOS camera #2
count = 0
current = 0
for val in df['oos2']:
    if val != current:
        count = count + 1
        current = val
print("Number of OOS image trigger changes / trigger highs encountered: ",count, count/2)
print(sum(df['ldm']))


# Read the timeline file where we manually maintain important events
imgcalib = pd.read_excel(filename_timeline)


# Calculate differential calibration from that timeline
calib = imgcalib[imgcalib.time_stamp.notnull()]
calib = calib[calib['OOS image#'].notnull()]
n_OOS_images = 18437
dOOSdt = n_OOS_images / (list(calib['time_stamp'])[-1] - list(calib['time_stamp'])[0])

oos_images_per_timestep = n_OOS_images / (list(calib['time_stamp'])[-1] - list(calib['time_stamp'])[0])
print('Average OOS images per timestep: ',oos_images_per_timestep)

print('Calibration points time_stamp to OOS image# from event timeline excel file:')
print('t0 ... t1                   (OOS#0 - OOS#1):     images/time_step')
first = 1
for t,img in zip(calib['time_stamp'],calib['OOS image#']):
    if first == 1:
        first = 0
        last_t = t
        last_img = img
        continue
    print(last_t, ' - ',t, '(',last_img, ' _ ',img,'): ',(img-last_img) / (t-last_t))
    last_t = t
    last_img = img

# Calibration, matching time_stamp to OOS image# (and reverse)
def get_last_calib(X, reverse=False):
    global calib
    listlastt = list()
    listlastimg = list()
    for item in X:
        lastt = 0
        lastimg = 0
        for t,img in zip(calib['time_stamp'],calib['OOS image#']):
            if not reverse:
                if t < item:
                    lastt = t
                    lastimg = img
            else:
                if img < item:
                    lastt = t
                    lastimg = img
        listlastt = lastt
        listlastimg = lastimg
    return (listlastt, listlastimg)

# convert time_stamp to OOS image#
def timestep_to_oosimg(X):
    global calib
    global n_OOS_images
    global dOOSdt

    (lastt, lastimg) = get_last_calib(X)
    return (X - lastt) * dOOSdt + lastimg

# convert OOS image# to time_stamp
def oosimg_to_timestep(X):
    global calib
    global n_OOS_images
    global dOOSdt

    (lastt, lastimg) = get_last_calib(X, reverse=True)
    return (X - lastimg) / dOOSdt + lastt


t_LDM_start  = 2263444
t_LDM_end    = 2635588
n_LDM_images = 372348

def ldmimg_to_timestep(X):
    global t_LDM_start
    global t_LDM_end
    global n_LDM_images

    return X * (t_LDM_end - t_LDM_start) / n_LDM_images + t_LDM_start

def timestep_to_ldmimg(X):
    global t_LDM_start
    global t_LDM_end
    global n_LDm_images

    return (X - t_LDM_start) * n_LDM_images / (t_LDM_end - t_LDM_start)



# convert timestamp in 1000Hz logfile to OOS image assuming continuous,
# evenly-spaced aquisition
t_first_oos = 2263332
t_last_oos  = 2635588
deltat_per_oos_img = (t_last_oos - t_first_oos) / n_OOS_images

def timestamp_to_oosimg(vec_t):
    global t_first_oos
    global t_last_oos
    global n_OOS_images
    global deltat_per_oos_img

    rval = vec_t
    for i,t in enumerate(vec_t):
        if (vec_t[i] < t_first_oos):
            rval[i] = np.nan
        else:
            # OOS images were taken till the end
            t_OOS = t - t_first_oos
            rval[i] = t_OOS /deltat_per_oos_img
    return rval

def oosimg_to_timestamp(vec_n):
    global t_first_oos
    global t_last_oos
    global n_OOS_images
    global deltat_per_oos_img

    rval = vec_n
    for i,n in enumerate(vec_n):
        if (n < 1):
            rval[i] = np.nan
        elif (n > n_OOS_images):
            rval[i] = t_last_oos
        else:
            rval[i] = vec_n[i] * deltat_per_oos_img + t_first_oos
    return rval


# peltier element pairs:
# OOS2 / XZ:
#   pair_x = [(2,4),(3,5)] --> x
# OOS1 / YZ and LDM (oblique by 30°)
#   pair_y = [(6,8),(7,9)] --> y
#   pair_z  = (10,1) --> z
# --> column numbers for pairs:

deltaT_x1 = df['TC4'] - df['TC2']
deltaT_x2 = df['TC5'] - df['TC3']
deltaT_y1 = df['TC8'] - df['TC6']
deltaT_y2 = df['TC9'] - df['TC7']
deltaT_z  = df['TC1'] - df['TC10']

deltaTs = [deltaT_x1, deltaT_x2, deltaT_y1, deltaT_y2, deltaT_z]
plot_names = ['x1', 'x2', 'y1', 'y2', 'z']

filter_sizes = [50,500]
filter_size= 50
plot_colors = ['blue', 'red']

from matplotlib import gridspec

image_ranges = [(0,370000), (31107,43907), (51507,65307), (72507,86407), (93907,107407)]

cm = 1/2.54

for name, deltaT in zip(plot_names, deltaTs):

    fig = plt.figure(figsize=(30*cm, 20*cm))
    plt.title(str(deltaT))
    gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])
    ax0 = plt.subplot(gs[0])
    ax0.set_title(name)
    ax0.set_xlabel('time [ms]')
    ax0.set_ylabel('temperature difference [K]')
    ax0.set_ylim(-2,2)
    secx = ax0.secondary_xaxis('top', functions=(timestep_to_ldmimg, ldmimg_to_timestep))
    secx.set_xlabel('LDM image #')
    ax1 = plt.subplot(gs[1], sharex = ax0)
    ax1.set_ylabel('residual temperature T- <T_500ms> [K]')
    ax1.set_ylim(-0.25,0.25)


    ax0.plot(df['time_stamp'], deltaT, color='lightgrey', label='original')
    for plot_color, filter_size in zip(plot_colors, filter_sizes):
        deltaT_smooth = np.convolve(deltaT, np.ones(filter_size) / filter_size, mode='same')
        dT, = ax0.plot(df['time_stamp'], deltaT_smooth, color=plot_color, label=str('smooth{0:3d}'.format(filter_size)))
        res = deltaT - deltaT_smooth
        resT, = ax1.plot(df['time_stamp'], res, color=plot_color)
        ax0.legend(loc='upper right')
        # ax0.legend(loc='upper right', color=['lightgrey, red, blue'], labels=['original', 'smooth 500ms', 'smooth 50ms'])

    plt.subplots_adjust(hspace=.0)

    for image_range in image_ranges:
        ax0.set_xlim(ldmimg_to_timestep(image_range[0]),ldmimg_to_timestep(image_range[1]))
        savefilename = str('{0}_{1:06d}-{2:06d}.png'.format(name, image_range[0], image_range[1]))
        plt.savefig(savefilename)

    plt.show()



# dT_50,  = ax0.plot(df['time_stamp'], deltaT_x1_smooth_50,  color='blue')
# dT_500, = ax0.plot(df['time_stamp'], deltaT_x1_smooth_500, color='red')
# ax0.set_xlabel('time [ms]')
# ax0.set_ylabel('temperature difference [K]')
# secx = ax0.secondary_xaxis('top', functions=(timestep_to_ldmimg, ldmimg_to_timestep))
# secx.set_xlabel('OOS image #')

# ax1 = plt.subplot(gs[1], sharex = ax0)
# resT_x1_50,  = ax1.plot(df['time_stamp'], res_x1_50,  color='blue')
# resT_x2_500, = ax1.plot(df['time_stamp'], res_x1_500, color='red')
# ax1.set_ylabel('residual temperature T- <T_500ms> [K]')

# plt.subplots_adjust(hspace=.0)
# plt.show()


# deltaT_x1_smooth_50 = np.convolve(deltaT_x1, np.ones(filter_size) / filter_size, mode='same')
# deltaT_x1_smooth_500 = np.convolve(deltaT_x1, np.ones(500) / 500, mode='same')
# res_x1_500 = deltaT_x1 - deltaT_x1_smooth_500
# res_x1_50 = deltaT_x1 - deltaT_x1_smooth_50



# # Make the plot for everything. You can manually zoom-in and save partial images
# fig1,ax1 = plt.subplots()
# ax1.set_xlabel('time [ms]')
# ax1.set_ylabel('temperature gradient')
# # ax1.set_ylim((-0.2, 2.2))
# ax1.plot(df['time_stamp'], deltaT_x1, color='red')
# ax1.plot(df['time_stamp'], deltaT_x1_smooth, color='darkblue')
# ax1.plot(df['time_stamp'], deltaT_x1_smooth500, color='black')
# ax1.set_ylim(-1,1)
# # ax1.plot(df['time_stamp'], df['TC2'] + 0.1, color='lightcoral')
# # ax1.plot(df['time_stamp'], df['TC3'] + 0.2, color='darkred')
# # ax1.plot(df['time_stamp'], df['TC4'] + 0.3, color='chocolate')
# # ax1.plot(df['time_stamp'], df['TC5'] + 0.4, color='darkorange')
# # ax1.plot(df['time_stamp'], df['TC6'] + 0.5, color='tan')
# # ax1.plot(df['time_stamp'], abs(df['Uvm1'])/14, color='blue')
# # ax1.plot(df['time_stamp'], abs(df['Uvm2'])/14, color='navy')
# ax1.legend()
# ax2 = ax1.twinx()
# ax2.set_ylim(-1.5,0.5)
# ax2.set_ylabel('residual temperature T- <T_500ms>')
# ax2.plot(df['time_stamp'], res_x1_500, color='lightblue')
# ax2.plot(df['time_stamp'], res_x1_50, color='blue')
# # ax2.plot(df['time_stamp'], abs(df['Uvm2'])/14, color='navy')
# # ax2.legend()

# # Add a secondary x-axis showing the OOS image #
# secx = ax1.secondary_xaxis('top', functions=(timestep_to_ldmimg, ldmimg_to_timestep))
# secx.set_xlabel('OOS image #')

# fig1.tight_layout()
# plt.show()



# from matplotlib import gridspec
# fig = plt.figure()
# gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])

# ax0 = plt.subplot(gs[0])
# dT_50,  = ax0.plot(df['time_stamp'], deltaT_x1_smooth_50,  color='blue')
# dT_500, = ax0.plot(df['time_stamp'], deltaT_x1_smooth_500, color='red')
# ax0.set_xlabel('time [ms]')
# ax0.set_ylabel('temperature difference [K]')
# secx = ax0.secondary_xaxis('top', functions=(timestep_to_ldmimg, ldmimg_to_timestep))
# secx.set_xlabel('OOS image #')

# ax1 = plt.subplot(gs[1], sharex = ax0)
# resT_x1_50,  = ax1.plot(df['time_stamp'], res_x1_50,  color='blue')
# resT_x2_500, = ax1.plot(df['time_stamp'], res_x1_500, color='red')
# ax1.set_ylabel('residual temperature T- <T_500ms> [K]')

# plt.subplots_adjust(hspace=.0)
# plt.show()
