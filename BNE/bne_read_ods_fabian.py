#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 10:34:32 2018
Read an ODS file for the BNE experiments by the Bachelor Student Fabian Helms

@author: ingo
"""
from BNE.ods_experiment_table import ods_experiment_table
from BNE.bne_config import bne_config
from tools.cast_lists import one_over_x

import numpy as np
from math import pi

class bne_read_ods_fabian(ods_experiment_table):
    def __init__(self):

        translate_dict = {
            'Zeile': {
                    'new_header': 'exp_id',
                    'type':       'str',
                    'prefix':     'fabian-',
                },
            'Zeit/ s': {
                    'new_header': 'tap_duration',
                    'type':       'float',
                    'conversion': 1.0,
                    },
            'Schüttelung/ m/s^2': {
                    'new_header': 'acc_excitation',
                    'type':       'float',
                    'conversion': 1.0,
                    },
            'Geschwindigkeit1/ m/s': {
                    'new_header': 'v1',
                    'type':       'float',
                    },
            'Geschwindigkeit2': {
                    'new_header': 'v2',
                    'type':       'float',
                    },
            'Geschwindigkeit3': {
                    'new_header': 'v3',
                    'type':       'float',
                    },
            'Geschwindigkeit4': {
                    'new_header': 'v4',
                    'type':       'float',
                    },
            'Geschwindigkeit5': {
                    'new_header': 'v5',
                    'type':       'float',
                    },
            'Geschwindigkeit6': {
                    'new_header': 'v6',
                    'type':       'float',
                    },
            'Geschwindigkeit7': {
                    'new_header': 'v7',
                    'type':       'float',
                    },
            'g': {
                    'new_header': 'ambient_g',
                    'type':       'float',
                    'conversion': 1.0,
                    },
            'Bildzahl1': { # These are counted twice for experimental reasons
                    'new_header': 'taps1',
                    'type':       'int',
                    'conversion': 0.5,
                },
            'Bildzahl2': { # These are counted twice for experimental reasons
                    'new_header': 'taps2',
                    'type':       'int',
                    'conversion': 0.5,
                },
            'Bildzahl3': { # These are counted twice for experimental reasons
                    'new_header': 'taps3',
                    'type':       'int',
                    'conversion': 0.5,
                },
            'Bildzahl4': { # These are counted twice for experimental reasons
                    'new_header': 'taps4',
                    'type':       'int',
                    'conversion': 0.5,
                },
            'Bildzahl5': { # These are counted twice for experimental reasons
                    'new_header': 'taps5',
                    'type':       'int',
                    'conversion': 0.5,
                },
            'Bildzahl6': { # These are counted twice for experimental reasons
                    'new_header': 'taps6',
                    'type':       'int',
                    'conversion': 0.5,
                },
            'Bildzahl7': { # These are counted twice for experimental reasons
                    'new_header': 'taps7',
                    'type':       'int',
                    'conversion': 0.5,
                },
            'Frequenz/ Hz': {
                    'new_header': 'unused_frequency',
                    'type':       'float',
                    'conversion': 1.0 / (2*pi),
                },
            'Amplitude/ m': {
                    'new_header': 'unused_amplitude',
                    'type':       'float',
                    'conversion': 1.0,
                },
            'gamma':     {
                    'new_header': 'unused_gamma',
                    'type':       'float',
                    'conversion': 1.0,
                },
            'S':         {'new_header': 'unused_S'},
            'L':         {'new_header': 'unused_L'},
            'v1*':       {'new_header': 'unused_v1*'},
            'v2*':       {'new_header': 'unused_v2*'},
            'v3*':       {'new_header': 'unused_v3*'},
            'v4*':       {'new_header': 'unused_v4*'},
            'v5*':       {'new_header': 'unused_v5*'},
            'v6*':       {'new_header': 'unused_v6*'},
            'v7*':       {'new_header': 'unused_v7*'},
            'Spannung Hoch/ V': {'new_header': 'unused'},
            'Fehler Spannung Hoch': {'new_header': 'unused'},
            'Spannung Runter/ V': {'new_header': 'unused'},
            'Fehler Spannung Runter': {'new_header': 'unused'},
            'Intervallänge': {'new_header': 'unused_intervall'},
            'Zeitfehler': {'new_header': 'unused'},
            'Fehler Frequenz': {'new_header': 'unused'},
            'Beschleunigung Hoch/ m/s^2': {'new_header': 'unused'},
            'Fehler Beschleunigung Hoch': {'new_header': 'unused'},
            'Beschleunigung Runter/ m/s^2': {'new_header': 'unused'},
            'Fehler Schüttelung': {'new_header': 'unused'},
            'Null Schüttelung/ m/s^2': {'new_header': 'unused'},
            'Fehler Null Schüttelung': {'new_header': 'unused'},
            'Fehler Amplitude': {'new_header': 'unused'},
            'Fehler Gamma': {'new_header': 'unused'},
            'Fehler S': {'new_header': 'unused'},
            'S^0,45*L^0,82': {'new_header': 'unused'},
            'Fehler Z5050': {'new_header': 'unused'},
            's^-0.0391': {'new_header': 'unused'},
            'Fehler Z5052': {'new_header': 'unused'},
            'S^0,1275': {'new_header': 'unused'},
            'Fehler Z5054': {'new_header': 'unused'},
            'Fehler v1*': {'new_header': 'unused'},
            'Fehler v2*': {'new_header': 'unused'},
            'Fehler v3*': {'new_header': 'unused'},
            'Fehler v4*': {'new_header': 'unused'},
            'Fehler v5*': {'new_header': 'unused'},
            'Fehler v6*': {'new_header': 'unused'},
            'Fehler v7*': {'new_header': 'unused'},
            'Fehler Geschwindigkeit1': {'new_header': 'unused'},
            'Fehler Geschwindigkeit2': {'new_header': 'unused'},
            'Fehler Geschwindigkeit3': {'new_header': 'unused'},
            'Fehler Geschwindigkeit4': {'new_header': 'unused'},
            'Fehler Geschwindigkeit5': {'new_header': 'unused'},
            'Fehler Geschwindigkeit6': {'new_header': 'unused'},
            'Fehler Geschwindigkeit7': {'new_header': 'unused'},
            }

#        filename = PROJECT_PATH + "TestImport.ods"
        filename = bne_config.get('project_path') + bne_config.get('filename_data_fabian')
        sheet = bne_config.get('sheetname_data_fabian')

        super().__init__(filename, sheet, translate_dict, experiments_in_columns = False)

        self.decimal_sep = ','



    def get_dict_of_lists(self):
        data = super().get_dict_of_lists()

        n_exp = len(next(iter(data.values())))
        self.data['origin'] = ['Fabian' for _ in range(n_exp)]
        self.data['bead_radius'] = [bne_config.get('bead_radius') for _ in range(n_exp)]
        self.data['frequency'] = 1 / np.array(self.data['tap_duration'], dtype='float')

        # Amplitude derived from data for excitation acceleration See the calculation from 1st Oct. 2018
        # for a rectangular acceleration profile (full tap)
        self.data['amplitude'] = [a / (4*f*f) for a,f in zip(self.data['acc_excitation'],self.data['frequency'])]
        self.data['rel_excitation'] = [a / (bne_config.get('g') * gamb) for a,gamb in zip(self.data['acc_excitation'],self.data['ambient_g'])]

        return self.data
