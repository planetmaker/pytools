#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 11:03:16 2018

@author: ingo
"""

import cv2

def rotate_image(img, angle=90, center=None):
    height, width, channels = img.shape
    if center == None:
        # this is strange and maybe a bug in cv2
        # TODO: this also likely breaks when rotating from wide images to high ones
        center = (width/2, width/2)
    M = cv2.getRotationMatrix2D(center, angle, 1)
    ret = cv2.warpAffine(img, M, (height, width))
    return ret