#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 11:01:13 2018

@author: ingo
"""
import numpy as np
import glob

from BNE.ods_experiment_table import ods_experiment_table
from BNE.bne_config import bne_config

from BNE.single_stage_programme import single_stage_programme, stage_programme_names

def v_from_taps(fill_height, frequency, taps):
    try:
        retval = fill_height * frequency / taps
    except:
        retval = np.NaN

    return retval

class bne_read_ods_ingo(ods_experiment_table):
    def __init__(self):

        translate_dict = {
                'exp.no.': {
                        'new_header': 'exp_id',
                    },
                'ambient[Earth G]': {
                        'new_header': 'ambient_g',
                        'type':       'float',
                        'conversion': 1.0
                    },
                'excitation[amb. G]': {
                        'new_header': 'rel_excitation',
                        'type':       'float',
                        'conversion': 1.0
                    },
                'Nut Dia. [mm]': {
                        'new_header': 'nut_radius',
                        'type':       'float',
                        'conversion': 0.001,
                    },
                'duration1 [taps]': {
                        'new_header': 'taps1',
                        'type':       'int',
                    },
                'duration2 [taps]': {
                        'new_header': 'taps2',
                        'type':       'int',
                    },
                'duration3 [taps]': {
                        'new_header': 'taps3',
                        'type':       'int',
                    },
                'duration4 [taps]': {
                        'new_header': 'taps4',
                        'type':       'int',
                    },
                'duration5 [taps]': {
                        'new_header': 'taps5',
                        'type':       'int',
                    },
                'duration6 [taps]': {
                        'new_header': 'taps6',
                        'type':       'int',
                    },
                'duration7 [taps]': {
                        'new_header': 'taps7',
                        'type':       'int',
                    },
                'Programme': {
                        'new_header': 'stage_programme',
                    },
                'containerdia. [cm]': {
                        'new_header': 'container_radius',
                        'type':       'float',
                        'conversion': 0.01
                    }
            }
        filename = bne_config.get('project_path') + bne_config.get('filename_data_ingo')
        sheet = bne_config.get('sheetname_data_ingo')

        super().__init__(filename, sheet, translate_dict, True)

        self.data_row_start = 1
        self.decimal_sep = '.'

    def get_dict_of_lists(self):
        data = super().get_dict_of_lists()

        n_exp = len(next(iter(data.values())))
        self.data['origin'] = ['Ingo' for _ in range(n_exp)]
        self.data['bead_radius'] = [bne_config.get('bead_radius') for _ in range(n_exp)]
        self.data['amplitude'] = [bne_config.get('amplitude_ingo') for _ in range(n_exp)]
        self.data['fill_height'] = [bne_config.get('fill_height_ingo') for _ in range(n_exp)]

        # read the info about the programmes
        stage_programmes = stage_programme_names(bne_config.get('project_path') + bne_config.get('filename_stage_programmes'))
        stage_programmes.read_file()
        stage_programmes.get_programme_info()
        prg_name_dict = stage_programmes.get_programmes_as_dict()

        # obtain the acceleration data for each programme and analyse them
        for prg,val in prg_name_dict.items():
            pattern = val.get('filename_pattern')
            filenames = glob.glob(bne_config.get('project_path') + bne_config.get('sensor_path') + pattern)
            # print("{}: ".format(prg)," ",filenames)
            # print(val)
            if len(filenames) == 0:
                continue
            acc_prg = single_stage_programme(prg, filenames[0])
            acc_prg.read_by_filename()

            acc_prg.extract_data(None, val.get('duration'), val.get('acc_rise_times'))
            # DEBUG
            # acc_prg.show_data()
            prg_name_dict[prg]['frequency'] = acc_prg.get_frequency()

        self.data['frequency'] = [np.NaN for _ in range(n_exp)]
        for i,pname in enumerate(self.data['stage_programme']):
            try:
                self.data['frequency'][i] = prg_name_dict.get(pname).get('frequency')
            except:
                pass

        for v,f,tap in zip(['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7'],
                           ['frequency' for _ in range(7)],
                           ['taps1', 'taps2', 'taps3', 'taps4', 'taps5', 'taps6', 'taps7']):
            self.data[v] = [v_from_taps(fill_height, f, t) for t,f,fill_height in zip(self.data[tap],self.data['frequency'],self.data['fill_height'])]
        self.data['vmax'] = [max(v1,v2,v3,v4,v5,v6,v7) for v1,v2,v3,v4,v5,v6,v7 in zip(self.data.get('v1'), self.data.get('v2'), self.data.get('v3'), self.data.get('v4'), self.data.get('v5'), self.data.get('v6'), self.data.get('v7'))]


        return self.data