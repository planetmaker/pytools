#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 11:19:25 2018

@author: ingo
"""
from os.path import expanduser

PROJECT_PATH = expanduser("~") + "/icaps/BNE/"

bne_config = {
        'code_path': expanduser("~") + "/idltools/BNE",
        'project_path': expanduser("~") + "/icaps/BNE/",
        'sensor_path': "sensor/",
        'plot_path': "plots/",
        'filename_stage_programmes': "BNE2_programme_info.ods",
        'sheetname_stage_programmes': u'BNE2_programme_info',
        'filename_data_yamada': "T.M.Yamada_2014_data.ods",
        'sheetname_data_yamada': u'T.M.Yamada_2014_data',
        'filename_data_fabian': "/BachelorArbeitFabian/Geschwindigkeiten_181008.ods",
        'sheetname_data_fabian': u'Tabelle1',
        'filename_data_ingo': "BNE_overview.ods",
        'sheetname_data_ingo': u'Experimente',
        'g': 9.81,
        'fill_height_ingo': 0.06,
        'amplitude_ingo':   0.02,
        'bead_radius':      0.001,
        }