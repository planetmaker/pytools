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

def image_ranges_2_timestamps(image_ranges):
    start_timestamps = list()
    for image_range in image_ranges:
        start_timestamps.append((ldmimg_to_timestep(image_range[0]), ldmimg_to_timestep(image_range[1])))

    return start_timestamps

def timestamps_2_datapoints(timestamps):
    datapoints = list()
    for timestamp in timestamps:
        datapoint = min(df['time_stamp'] > timestamp)
        datapoints.append(datapoint)

    return datapoints

def integrate(df, integration_ranges):
    df['posx'] = np.nan
    df['posy'] = np.nan
    df['posz'] = np.nan
    dx = 0
    dy = 0
    dz = 0
    n_ranges = len(integration_ranges)
    current_range = 1 # first ignored as full range

    this_range = integration_ranges[current_range]
    start = this_range[0]
    end = this_range[1]
    for index, row in df.iterrows():
        if (row['time_stamp'] > end):
            dx = 0
            dy = 0
            dz = 0
            current_range += 1
            if current_range >= n_ranges:
                return
            this_range = integration_ranges[current_range]
            start = this_range[0]
            end = this_range[1]
        else:
            if (row['time_stamp'] < start):
                pass
            else:
                dx += row['dx']
                dy += row['dy']
                dz += row['dz']
                (df['posx'])[index] = dx
                (df['posy'])[index] = dy
                (df['posz'])[index] = dz

    return


# peltier element pairs:
# OOS2 / XZ:
#   pair_x = [(2,4),(3,5)] --> x
# OOS1 / YZ and LDM (oblique by 30°)
#   pair_y = [(6,8),(7,9)] --> y
#   pair_z  = (10,1) --> z
# --> column numbers for pairs:

df['deltaT_x1'] = df['TC4'] - df['TC2']
df['deltaT_x2'] = df['TC5'] - df['TC3']
df['deltaT_y1'] = df['TC8'] - df['TC6']
df['deltaT_y2'] = df['TC9'] - df['TC7']
df['deltaT_z']  = df['TC1'] - df['TC10']
df['deltaT_x'] = (df['deltaT_x1'] + df['deltaT_x2'] ) / 2
df['deltaT_y'] = (df['deltaT_y1'] + df['deltaT_y2'] ) / 2

# Calculate the averaged time over 500 data points (=500 milliseconds)
trend_filter_length = 125 * 4 # Datapoints to average over. Timesteps are in 4ms increments (thus * 4 is in milliseconds)
coupling_time = 6
coupling_smooth = int(np.ceil(coupling_time / 4))
# distances according to CDR document "IPESR-RP-00032-QS_B0_ICAPS Sounding Rocket Experiment design description.pdf" p36
d_xy = 0.047 # inner diameter of large rings
d_z  = 0.047 # height difference between small rings

df['dT_x_smooth500'] = np.convolve(df['deltaT_x'], np.ones(trend_filter_length) / trend_filter_length, mode='same')
df['dT_y_smooth500'] = np.convolve(df['deltaT_y'], np.ones(trend_filter_length) / trend_filter_length, mode='same')
df['dT_z_smooth500'] = np.convolve(df['deltaT_z'], np.ones(trend_filter_length) / trend_filter_length, mode='same')

# Residuals between the actual temperature and the trend over 500 milliseconds
df['res_dT_x'] = df['deltaT_x'] - df['dT_x_smooth500']
df['res_dT_y'] = df['deltaT_y'] - df['dT_y_smooth500']
df['res_dT_z'] = df['deltaT_z'] - df['dT_z_smooth500']

# smooth data by the coupling time so that we don't introduce spurious accelerations
df['res_dT_x_smooth'] = np.convolve(df['res_dT_x'], np.ones(coupling_smooth) / coupling_smooth, mode='same')
df['res_dT_y_smooth'] = np.convolve(df['res_dT_y'], np.ones(coupling_smooth) / coupling_smooth, mode='same')
df['res_dT_z_smooth'] = np.convolve(df['res_dT_z'], np.ones(coupling_smooth) / coupling_smooth, mode='same')

df['gradT_x'] = df['res_dT_x_smooth'] / d_xy
df['gradT_y'] = df['res_dT_y_smooth'] / d_xy
df['gradT_z'] = df['res_dT_z_smooth'] / d_z

# velocity introduced by residualt temperature variations:
v_CMS = 55e-6 # m/s/ (K/m)
df['vx_res_CMS'] = df['gradT_x'] * v_CMS
df['vy_res_CMS'] = df['gradT_y'] * v_CMS
df['vz_res_CMS'] = df['gradT_z'] * v_CMS

# Calculate the time differences between data rows in seconds
df['dt'] = df['time_stamp'].diff() / 1000

# Calculate the movement distance between timesteps
df['dx'] = df['vx_res_CMS'] * df['dt']
df['dy'] = df['vy_res_CMS'] * df['dt']
df['dz'] = df['vz_res_CMS'] * df['dt']

image_ranges = [(0,370000), (31107,43907), (51507,65307), (72507,86407), (93907,107407)]
integration_ranges = image_ranges_2_timestamps(image_ranges)

integrate(df, integration_ranges)

# plot_names = ['vx_res_CMS', 'vy_res_CMS', 'vz_res_CMS']
# plots = dict()
# plotsx = dict()
# plotsx['plots'] = ('res_dT_x','res_dT_x_smooth', 'gradT_x','vx_res_CMS','posx')
# plotsx['title'] =
plot_names = [\
              ('res_dT_x','res_dT_x_smooth', 'gradT_x','vx_res_CMS','posx'), \
              ('res_dT_y','res_dT_y_smooth', 'gradT_y','vy_res_CMS','posy'), \
              ('res_dT_z','res_dT_z_smooth', 'gradT_z','vz_res_CMS','posz') \
                  ]


from matplotlib import gridspec
cm = 1/2.54

for name in plot_names:

    fig = plt.figure(figsize=(30*cm, 20*cm))
    plt.title(name)
    gs = gridspec.GridSpec(4, 1, height_ratios=[2,2,2,2])

    ax0 = plt.subplot(gs[0])
    ax0.set_title(name)
    ax0.set_xlabel('time [ms]')
    ax0.set_ylabel(name[0])
    ax0.plot(df['time_stamp'], df[name[0]])
    ax0.plot(df['time_stamp'], df[name[1]],color='red')
    ax0.set_ylim(-0.25,0.25)

    ax1 = plt.subplot(gs[1], sharex = ax0)
    ax1.set_ylabel(name[2])
    #ax1.set_ylim(-0.25,0.25)
    ax1.plot(df['time_stamp'], df[name[2]])
    ax1.set_ylim(-5,5)

    ax2 = plt.subplot(gs[2], sharex = ax0)
    ax2.set_ylabel(name[3])
    #ax2.set_ylim(-0.25,0.25)
    ax2.plot(df['time_stamp'], df[name[3]])
    ax2.set_ylim(-0.00025,0.00025)

    ax3 = plt.subplot(gs[3], sharex = ax0)
    ax3.set_ylabel(name[4])
    #ax3.set_ylim(-0.25,0.25)
    ax3.plot(df['time_stamp'], df[name[4]])
    ax3.set_ylim(-0.0001,0.0001)

    plt.subplots_adjust(hspace=.0)
    plt.show()


    for image_range in image_ranges:
        ax0.set_xlim(ldmimg_to_timestep(image_range[0]),ldmimg_to_timestep(image_range[1]))
        savefilename = str('{0}_{1:06d}-{2:06d}.png'.format(name[4], image_range[0], image_range[1]))
        plt.savefig(savefilename)

    plt.show()



# ====================================================================
# Plotting temperature differences and residuals wrt means

deltaTs = [df['deltaT_x1'], df['deltaT_x2'], df['deltaT_y1'], df['deltaT_y2'], df['deltaT_z']]
plot_names = ['x1', 'x2', 'y1', 'y2', 'z']

filter_sizes = np.ceil([12.5,125] * 4).astype(int)
filter_size= np.ceil(12.5*4)
plot_colors = ['blue', 'red']

from matplotlib import gridspec


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

# ====================================================================
# Create the

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
