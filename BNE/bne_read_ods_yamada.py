#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 11:01:13 2018

@author: ingo
"""
import numpy as np

from ods_experiment_table import ods_experiment_table
from bne_config import bne_config

class bne_read_ods_yamada(ods_experiment_table):
    def __init__(self):

        translate_dict = {
                'Amplitude': {
                        'new_header': 'amplitude',
                        'type':       'float',
                        'conversion': 0.001,
                    },
                'Frequency': {
                        'new_header': 'frequency',
                        'type':      'float',
                    },
                'Grain_diameter': {
                        'new_header': 'bead_radius',
                        'type':       'float',
                        'conversion': 0.0005,
                    },
                'Vessel_radius': {
                        'new_header': 'container_radius',
                        'type':       'float',
                        'conversion': 0.001,
                    },
                'Granular_bed_Height': {
                        'new_header': 'fill_height',
                        'type':       'float',
                        'conversion': 0.001,
                    },
                'v_zmax': {
                        'new_header': 'vmax',
                        'type':       'float',
                        'conversion': 0.001,
                    },
                'g': {
                        'new_header': 'ambient_g',
                        'type':       'float',
                        'conversion': 0.001 / 9.81,
                    },
                'Gamma':     {
                        'new_header': 'rel_excitation',
                        'type':       'float',
                        'conversion': 1.0,
                    },
                'S':         {'new_header': 'unused_S'},
                'L':         {'new_header': 'unused_L'},
                'v_zmax_SD': {'new_header': 'unused_v_zmax_SD'},
                'v1*':       {'new_header': 'unused_v1*'},
                'v1*_SD':    {'new_header': 'unused_v1*_SD'}
                }
        filename = bne_config.get('project_path') + bne_config.get('filename_data_yamada')
        sheet = bne_config.get('sheetname_data_yamada')

        super().__init__(filename, sheet, translate_dict, True)

        self.data_row_start = 2
        self.decimal_sep = ','

    def get_dict_of_lists(self):
        data = super().get_dict_of_lists()

        n_exp = len(next(iter(data.values())))
        self.data['origin'] = ['Yamada' for _ in range(n_exp)]
        self.data['exp_id'] = ["{!s:>3}-Yamada".format(i+3) for i in range(n_exp)]

        # Filter out the lines w/o experiment info which will only contain NaN
        ambientg = np.array(data.get('ambient_g'))
        wo_nan = (np.where(np.isfinite(ambientg) == False))[0].tolist()
        for key,value in data.items():
            value = np.delete(value, wo_nan)
            data[key] = value

        return self.data
