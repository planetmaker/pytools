#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  6 11:03:16 2018

@author: ingo
"""

import cv2

def rotate_image(img):
    height, width, channels = img.shape
    M = cv2.getRotationMatrix2D((width/2, height/2), 90, 1)
    return cv2.warpAffine(img, M, (width,height))