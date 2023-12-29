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
        

radii = []
skiprows = 2
for i in range(5):
    if i > 0:
        skiprows = 1
    df = pd.read_excel(filename, engine="odf", skiprows=skiprows, sheet_name=i, decimal='.')
    # print(df)
    radii.extend(parse_radius(df['radius_km']))
    # print(radii)
    
count = [x for x in range(len(radii))]

fig,ax = plt.subplots()
ax.scatter(radii,count, marker='+', linewidth=1.0)
ax.set(xlim=(10,100000), ylim=(1,1000))
plt.yscale('log')
plt.xscale('log')
plt.title('size distribution of solar system bodies')
plt.xlabel('size [km]')
plt.ylabel('count bodies larger than size')
plt.show()