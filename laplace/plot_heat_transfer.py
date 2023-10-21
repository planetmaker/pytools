#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:24:51 2023

@author: ingo
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

import matplotlib.collections as mcol
from matplotlib.legend_handler import HandlerLineCollection, HandlerTuple
from matplotlib.lines import Line2D

raw_path = 'Nextcloud/TUBS/LAPLACE-CAD/subsystems_documentation/LDM_LongDistanceMicroscope/heat_transfer_measurements/raw_data/'

class Measurement(dict):
    # extended dictionary class for the description of the measurement (files). 
    # For simplicity some defaults are defined here
    def __missing__(self, key):
        if key == 'diff':
            return ('ch2','ch3')
        return None

def read_measurement_csv(filename, column_names = None):
    try:
        df = pd.read_csv(filename, sep = ',', encoding='latin1', skiprows=2)
    except:
        print("Reading failed: {}".format(filename))
        return None

    num_channels = (df.shape[1] - 1) // 2
    df2 = pd.DataFrame()
    for i in range(num_channels):
        name = str('ch{}').format(i+1)
        df2[name] = df.iloc[:,2*i+1] + df.iloc[:,2*i+2] / 100
   
    return df2

def plot_columns(title,filedata):
    
    filename = Path.home().joinpath(raw_path).joinpath(filedata['filename'])  # Replace with your file name

    try:
        df = pd.read_csv(filename, sep=filedata['sep'], decimal=filedata['decimal'],on_bad_lines='skip')
    except:
        df = pd.read_csv(filename, sep=filedata['sep'], decimal=filedata['decimal'])        
    
    print(list(df.columns))
    
    df.plot(x="time", y=["Chamber Cam", "Cam", "Chamber LED", "LED", "Ref"], title=title+": raw data", style='-', ylabel="temperature [°C]", xlabel="time [s]")
    
    
    df['delta Ref'] = (df.loc[0:, "Ref"] - df.at[filedata['tref'], "Ref"])
    df['delta Chamber'] = df.loc[0:, "Chamber Cam"] - df.at[filedata['tref'], "Chamber Cam"]
    df['delta Chamber LED'] = df.loc[0:, "Chamber LED"] - df.at[filedata['tref'], "Chamber LED"]
    df["deltaT Chamber Microscope"] = df["delta Chamber"] - df["delta Ref"]
    df["deltaT Chamber Ref"] = df["delta Chamber LED"] - df["delta Ref"]
    
    
    df.plot(x="time", y=["deltaT Chamber Microscope"], title=title, style='-', ylabel="temperature rise [°C]", xlabel="time [s]", ylim=filedata['deltaylim'])
    
def to_ref(df, ref_channel_name=None):
    if ref_channel_name is None:
        ref_channel_name = df.columns[0]
    ref_temperature = df[ref_channel_name][0]

    df2 = pd.DataFrame()

    for column in df:
        start_temperature = df[column][0]
        df2[column] = df[column] - start_temperature + ref_temperature
        
    return df2

def plot_with_difference(df, name_diff, yrange=None, diff_yrange=None, title=None, **kwargs):
    fig, (ax0,ax1) = plt.subplots(2, 1, sharex = True, figsize=(10.24,10.24), gridspec_kw=dict(height_ratios=[3,1]))
    # Remove vertical space between axes
    fig.subplots_adjust(hspace=0)
    num_rows = df.shape[0]
    t = [t/60 for t in range(num_rows)]
    
    # Plot each graph, and manually set the y tick values
    # l1, = ax0.plot(t, df[name_diff1], label=name_diff1)
    # l2, = ax0.plot(t, df[name_diff2], label=name_diff2)
    for column in df:
        ax0.plot(t, df[column], label=column)
    # ax0.plot(t, df[name_diff1], label=name_diff1)
    # ax0.plot(t, df[name_diff2], label=name_diff2)
    # ax0.legend([l1,l2])
    # ax0.legend([l1,l2],[name_diff1, name_diff2])
    # ax0.legend(handles=[l1,l2],loc='upper left',shadow=True)
    ax0.legend()
    ax0.grid(True, linestyle='-.')
    ax0.set_ylabel('temperature [°C]')
    
    ax1.plot(t, df[name_diff[0]] - df[name_diff[1]], label=str('Difference {} to {}').format(name_diff[0],name_diff[1]))
    ax1.set_xlabel('time [min]')
    ax1.set_ylabel('temp. diff [°c]')
    ax1.legend()
    
    if title is not None:
        ax0.set_title(title)
    if yrange is not None:
        ax0.yrange = yrange
    if diff_yrange is not None:
        ax1.yrange= diff_yrange
    
    plt.show()
    
    
    
measurements = dict()
# measurements['unmodified'] = {'filename': 'mikroskop_20230628.txt', 'sep':'\t', 'decimal':',', 'deltaylim':[-0.5,1.5], 'tref':750/6}
# measurements['250µm teflon at microscope, no fan, deflector'] =  {'filename': 'mikroskop_20230702.txt', 'sep': ',', 'decimal':'.', 'deltaylim':[-0.5,1.5], 'tref':750/6}
# measurements['250µm teflon at cam, no fan, no deflector'] = {'filename': 'mikroskop_20230712.txt', 'sep': '\t', 'decimal':',', 'deltaylim':[-0.5,1.5], 'tref':750}
# measurements['250µm teflon at cam, fan + deflector'] = {'filename': 'mikroskop_20230714.txt', 'sep': '\t', 'decimal':',', 'deltaylim':[-0.5,1.5], 'tref':750}
# measurements['500µm teflon at cam, no fan, no deflector'] = {'filename': 'mikroskop_20230719.txt', 'sep': '\t', 'decimal':',', 'deltaylim':[-0.5,1.5], 'tref':750}
# measurements['with chamber'] = {'filename': 'mikroskop_20230927a1.txt', 'sep': '\t', 'decimal':',', 'deltaylim':[-0.5,1.5], 'tref':750}

measurements['Cam Microscope cooled'] = Measurement(filename='mikroskop_20231019a1.csv')
measurements['LED'] = Measurement(filename='mikroskop_20231020a5.csv', diff=('ch1', 'ch4'))

#for k,v in measurements.items():
#    plot_columns(k,v)
# plot_columns('with chamber', measurements['with chamber'])


# datafilename = 'mikroskop_20231020a5.csv'
# filename = Path.home().joinpath(raw_path).joinpath(datafilename)

# df = pd.read_csv(filename, sep=',', encoding='latin1', skiprows=2)

# num_channels = (df.shape[1] - 1) // 2
# for i in range(num_channels):
#     name = str('ch{}').format(i+1)
#     df[name] = df.iloc[:,2*i+1] + df.iloc[:,2*i+2] / 100

# df = read_measurement_csv(filename)
# df.plot(title=datafilename,xlabel='time [s]',ylabel='temperature [°C]')

# dfstart = to_ref(df, ref_channel_name=None)
# plot_with_difference(dfstart, 'ch1', 'ch4', title=datafilename)

for name,measurement in measurements.items():
    filename = Path.home().joinpath(raw_path).joinpath(measurement['filename'])
    ref = measurement['ref']
    diff = measurement['diff']
    print(filename)
    df = read_measurement_csv(filename)
    dfstart = to_ref(df, ref_channel_name = ref)
    plot_with_difference(dfstart, diff, title=name)
    