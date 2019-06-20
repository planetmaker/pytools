#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 12:26:09 2018

@author: ingo
"""

import numpy as np

class BNE_experiment:
    data = {}

    def __init__(self):
        self.data = {}

    def set_property(self, name, value):
        self.data[name] = value

    def get_property(self, name):
        return self.data.get(name)

    def __repr__(self):
        try:
            exp_id = self.get_property('exp_id')
            s = "{}".format(exp_id)
            print(s)
        except:
            s = "undefined"

        return "<Class BNE_experiment: ID {}>".format(s)

    def __str__(self):
        try:
            exp_id = self.get_property('exp_id')
            s = "Experiment '{}':".format(exp_id)
        except:
            s = "Experiment with undefined exp_id:"

        for key, value in sorted(self.data.items()):
            s += "\n  {}: {}".format(key, value)

        return s


    def set_stage_programme(self, stage_programme):
        self.set_property('stage_programme', stage_programme)

    def set_taps(self, taps):
        self.set_property('taps', taps)

    def set_duration(self, duration):
        self.set_property('duration', duration)

    def set_container(self, container):
        self.set_property('container', container)

    def set_parameters(self, g, excitation):
        self.set_property('ambient_g', g)
        self.set_property('relative_excitation', excitation)

    def get_duration(self, sphere_no):
        try:
            duration = self.get_property('duration')
            try:
                return duration[sphere_no]
            except:
                return np.NaN
        except:
            return np.NaN

    def get_fill_height(self):
        try:
            return self.get_property('fill_height')
        except:
            return np.NaN



    def get_mean_duration(self):
        return np.mean(self.get_property('duration'))

    def get_rise_velocity(self):
        duration = self.get_duration()
        height   = self.get_fill_height()
        if duration == np.NaN or height == np.NaN:
            return np.NaN

        v = duration
        for i,t in enumerate(duration):
            v[i] = height / t

        return v