#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 15:21:03 2018

@author: ingo
"""

from tools.ODSReader import ODSReader
from tools.cast_lists import list_to_float, list_to_int

import numpy as np

class ods_experiment_table:
    """
    Class which reads an ODS (OpenDocument) Table and converts it to usable
    data
    """
    filename = None
    sheet = None
    translate_dict = None
    experiments_in_columns = True
    raw_data = []
    data = {}
    data_row_start = 1
    decimal_sep = '.'

    def __init__(self, filename: str, sheet: str, translate_dict: dict, experiments_in_columns = True):
        self.filename = filename
        self.sheet = sheet
        self.translate_dict = translate_dict
        self.experiments_in_columns = experiments_in_columns
        self.data = {}
        self.raw_data = []
        self.data_row_start = 1
        self.decimal_sep = '.'

    def __str__(self):
        return "<read_ods_experiment_table>: {}".format(self.filename)

    def __repr__(self):
        return "<read_ods_experiment_table>: {}".format(self.filename)

    def read_by_row(self):
        doc = ODSReader(self.filename, clonespannedcolumns = True)
        table = doc.getSheet(self.sheet)

        # Now make sure that each line has the same length
        maxlen = max([len(line) for line in table])
        data = []
        for line in table:
            while len(line) < maxlen:
                line.append(None)
            data.append(line)

        return data

    def read(self):
        data = self.read_by_row()
        if self.experiments_in_columns:
            data = np.transpose(data)
        self.raw_data = data

    def translate(self):
        retdict = {}
        for i,line in enumerate(self.raw_data):
            header = line[0]
            if header is None:
                header = "Property {}".format(i+1)
            data = line[self.data_row_start:]
            if header in self.translate_dict:
                translation = self.translate_dict[header]
                if 'new_header' in translation:
                    header = translation['new_header']
                if 'type' in translation:
                    if translation['type'] == 'float':
                        data = list_to_float(data, default = np.NaN, decimal_sep = self.decimal_sep)
                    elif translation['type'] == 'int':
                        data = list_to_int(data, default = np.NaN, decimal_sep = self.decimal_sep)
                    elif translation['type'] == 'str':
                        if 'prefix' in translation:
                            data = [translation['prefix'] + str(item) for item in data]

                    if 'conversion' in translation:
                        data = [item * translation['conversion'] for item in data]
            retdict[header] = data

        self.data = retdict

    def get_dict_of_lists(self):
        assert(self.filename is not None)
        assert(self.sheet is not None)

        self.read()
        self.translate()

        return self.data

    def get_list_of_dicts(self):
        data = self.get_dict_of_lists()

        key, value = next(iter(data.items()))
        n_exps = len(value)
        exp_list = [{} for _ in range(n_exps)]
        for key, values in data.items():
            for i,item in enumerate(values):
                exp_list[i][key] = item

        return exp_list