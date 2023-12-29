#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 29 11:03:58 2023

@author: planetmaker
"""

import pandas as pd
import matplotlib.pyplot as plt

filename = 'solarsystem_bodies.ods'
numbers = '0123456789.'

def parse_radius(col_df) -> float():
    # print(col_df)
    col = []
    for strg in col_df:
        newstrg = ""
        if type(strg) == int:
            col.append(strg)
            continue
        for c in strg:
            if c in numbers:
                newstrg = newstrg + c
            else:
                if newstrg == "":
                    continue
                # print("strg:'{}', newstrg:'{}'".format(strg,newstrg))
                col.append(float(newstrg))
                break
        # print(col)
    return col
        
def filter_moons(df):
    dff = df[df['Type'].str.startswith('moon of')]
    print(dff)
    return dff

radii = []
skiprows = 2
for i in range(7):
    if i > 0:
        skiprows = 1
    df = pd.read_excel(filename, engine="odf", skiprows=skiprows, sheet_name=i, decimal='.')
    # print(df)
    radius = parse_radius(df['radius_km'])
    # Bodies smaller than 1km are given in m
    if i == 6:
        for j,r in enumerate(radius):
            radius[j] = r/1000
    radii.extend(radius)
    # print(radii)
    
count = [x for x in range(len(radii))]

fig,ax = plt.subplots()
ax.scatter(radii,count, marker='+', linewidth=1.0)
ax.set(xlim=(0.01,100000), ylim=(1,1000))
plt.yscale('log')
plt.xscale('log')
plt.title('size distribution of solar system bodies')
plt.xlabel('size [km]')
plt.ylabel('count bodies larger than size')
plt.show()

#only moons
moons = []
skiprows = 2
for i in range(7):
    if i > 0:
        skiprows = 1
    dff = pd.read_excel(filename, engine="odf", skiprows=skiprows, sheet_name=i, decimal='.')
    dff = filter_moons(dff)    
    # print(df)
    radius = parse_radius(dff['radius_km'])
    # Bodies smaller than 1km are given in m
    if i == 6:
        for j,r in enumerate(radius):
            radius[j] = r/1000
    moons.extend(radius)
    # print(radii)
    
countm = [x for x in range(len(moons))]

fig,ax = plt.subplots()
ax.scatter(moons,countm, marker='+', linewidth=1.0)
ax.set(xlim=(0.01,100000), ylim=(1,1000))
plt.yscale('log')
plt.xscale('log')
plt.title('size distribution of solar system moons')
plt.xlabel('size [km]')
plt.ylabel('count bodies larger than size')
plt.show()
