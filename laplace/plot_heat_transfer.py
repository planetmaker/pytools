#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:24:51 2023

@author: ingo
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


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
        name = column_names[i] if column_names is not None else str('ch{}').format(i+1)
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
    
    for column in df:
        ax0.plot(t, df[column], label=column)

    ax0.legend()
    ax0.grid(True, linestyle='-.')
    ax0.set_ylabel('temperature [°C]')
    
    ax1.plot(t, df[name_diff[0]] - df[name_diff[1]], label=str('Difference {} to {}').format(name_diff[0],name_diff[1]))
    ax1.set_xlabel('time [min]')
    ax1.set_ylabel('temp. diff [°c]')
    ax1.grid(True, linestyle='-.')
    ax1.legend()
    
    if title is not None:
        ax0.set_title(title)
    if yrange is not None:
        ax0.yrange = yrange
    if diff_yrange is not None:
        ax1.yrange= diff_yrange
    
    plt.show()
    
    
    
measurements = dict()

measurements['LED'] = Measurement(filename='mikroskop_20231020a5.csv', diff=('Light', 'Microscope'), names=['Microscope tube','Light','Microscope','Cam'])
measurements['Microscope cooled'] = Measurement(filename='mikroskop_20231019a1.csv', diff=('Microscope','Light'), names=['Microscope tube','Light','Microscope','Cam'])
measurements['Microscope cooled #2'] = Measurement(filename='mikroskop_20231017a3.csv', diff=('Microscope', 'Light'), names=['Microscope tube','Light','Microscope','Cam'])
measurements['Microscope'] = Measurement(filename='mikroskop_20231016a2.csv', diff=('Microscope','Light tube'), names=['Cam','Light tube','Microscope','Microscope tube'])

# measurements['Teflon 750µm'] = Measurement(filename='mikroskop_20230920a2.csv', diff=('Microscope','Ref'), names=['Cam','Unused','Ref','Microscope tube','Microscope'])
measurements['default'] = Measurement(filename='mikroskop_20230927a1.csv', diff=('Microscope','Light outside'), names=['Cam','Light outside','Microscope','Microscope tube'])

for name,measurement in measurements.items():
    filename = Path.home().joinpath(raw_path).joinpath(measurement['filename'])
    ref = measurement['ref']
    diff = measurement['diff']
    print("Processing: {}".format(measurement['filename']))
    df = read_measurement_csv(filename,column_names=measurement['names'])
    dfstart = to_ref(df, ref_channel_name = ref)
    plot_with_difference(dfstart, diff, title=name)
    