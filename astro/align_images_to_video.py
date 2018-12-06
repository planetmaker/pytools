#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 15:49:58 2018

@author: ingo
"""

path = "/home/ingo/ownCloud/planetmaker/sternwarte/jochen/Merkurtransit - jpg 09.05.2016/"
pattern = "LIGHT*jpg"

import cv2
import numpy as np
import glob, os

import sys
sys.path.append("../imaging/")
from detect_circles import detect_circles
from rotate_image import rotate_image
#from .imaging import detect_circles

#def align_images_to_video(path, pattern, output="out.mp4"):
os.chdir(path)
files = glob.glob(pattern)

img_info = dict()
for file in files:
    img = cv2.imread(path + file)
    try:
        width, height, channels = img.shape
    except AttributeError:
        print("Failed to read {}".format(file))
        continue
    thumb = cv2.resize(img, (int(0.2 * height), int(0.2 * width)), interpolation=cv2.INTER_CUBIC)
    height, width, channels = thumb.shape
    rotate = 0
    if height > width:
        thumb = rotate_image(thumb)
        rotate = 90
    circles = detect_circles(thumb)
    if circles is None:
        print("No circle found in {}".format(file))
        continue
    best = {'i':None, 'dist':0, 'x':None, 'y':None, 'r':None}
    for n,circle in enumerate(circles):
        print(circle)
        dist = min([width-circle[0][0],height-circle[0][1]])
        if dist > best.get('dist'):
            best = {
                    'i':n,
                    'dist':dist,
                    'x':circle[0][0],
                    'y':circle[0][1],
                    'r':circle[0][2],
                    }
    img_info[file] = {
            'width': width,
            'height': height,
            'channels': channels,
            'circles': circles,
            'rotate':rotate,
            'best': best,
            }

print(img_info)
# print(files)

cv2.circle(
        thumb, # image
        (img_info[file].get('best').get('x'), img_info[file].get('best').get('y')), # point (x,y)
        img_info[file].get('best').get('r'), # radius
        (0,255.0), # colour
        2 # linethickness
        )
cv2.circle(
        thumb,
        (img_info[file].get('best').get('x'), img_info[file].get('best').get('y')),
        2,
        (0,0.255),
        3
        )
cv2.imshow('circles', thumb)


#if __name__ == "__main__":
#    align_images_to_video(path, pattern)