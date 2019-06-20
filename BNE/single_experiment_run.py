#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 10:32:13 2018

@author: ingo
"""

class single_epxeriment_run:

    exp_id = 0
    path = ""

    def __init__(self):
        pass
#        self.exp_id = exp_id
#        self.path = path

    def __repr__(self):
        return "<Class Single Experiment Run: ID {} from '{}'>".format(self.exp_id,self.path)

    def __str__(self):
        s = "Exp. ID: {} from {}".format(self.exp_id, self.path)
        return s

    def set_id(self, exp_id):
        self.exp_id = exp_id

    def set_path(self, path):
        self.path = path

    def get_id(self):
        return(self.exp_id)

    def get_path(self):
        return(self.path)

