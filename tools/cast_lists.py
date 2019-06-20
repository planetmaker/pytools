#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 10:00:17 2018

@author: ingo
"""

def cast_to_float(s, default = None, decimal_sep = '.'):
    try:
        val = float(s.replace(decimal_sep, '.'))
    except (AttributeError, ValueError):
        val = default
    return val

def cast_to_int(s, default = None, decimal_sep = '.'):
    try:
        val = int(s.replace(decimal_sep, '.'))
    except (AttributeError, ValueError):
        val = default
    return val



def list_to_float(l: list, default = None, decimal_sep = '.'):
    ret_list = []
    for item in l:
        ret_list.append(cast_to_float(item, default, decimal_sep))

    return ret_list

def list_to_int(l: list, default = None, decimal_sep = '.'):
    ret_list = []
    for item in l:
        ret_list.append(cast_to_int(item, default, decimal_sep))

    return ret_list


def one_over_x(element, div_by_zero = None):
    try:
        val = 1 / element
    except ZeroDivisionError:
        val = div_by_zero
    return val

