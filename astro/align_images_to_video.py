#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 15:49:58 2018

@author: ingo
"""

path = "/home/ingo/ownCloud/planetmaker/sternwarte/jochen/Merkurtransit - jpg 09.05.2016/renamed/"
pattern = "LIGHT*jpg"

import cv2
import numpy as np
import glob, os

import sys
sys.path.append("../imaging/")
from detect_circles import detect_circles
from rotate_image import rotate_image
#from ..imaging import detect_circles
#from imaging import rotate_image

#def align_images_to_video(path, pattern, output="out.mp4"):
os.chdir(path)
files = sorted(glob.glob(pattern))

img_info = []
for file in files[350:353]:
    img = cv2.imread(path + file)
    try:
        width, height, channels = img.shape
    except AttributeError:
        print("Failed to read {}".format(file))
        continue
    thumb = cv2.resize(img, (int(0.2 * height), int(0.2 * width)), interpolation=cv2.INTER_CUBIC)
    height, width, channels = thumb.shape

    # Make sure that they are all in the same rotation state. That curiously is not the case by default.
    rotate = 0
    if height > width:
        rot = rotate_image(thumb)
        rotate = 90
        height, width, channels = rot.shape
    else:
        rot = thumb

    # Detect the circles and find the best.
    circles = detect_circles(rot)
    if circles is None:
        print("No circle found in {}".format(file))
        continue
    best = {'i':None, 'dist':0, 'x':None, 'y':None, 'r':None}
    for n,circle in enumerate(circles):
        dist = min([width-circle[0][0],height-circle[0][1]])
        if dist > best.get('dist'):
            best = {
                    'i':n,
                    'dist':dist,
                    'x':circle[0][0],
                    'y':circle[0][1],
                    'r':circle[0][2],
                    }
    img_info.append({
            'name':file,
            'width': width,
            'height': height,
            'channels': channels,
            'circles': circles,
            'rotate':rotate,
            'best': best,
            })

print(img_info)
# print(files)

# show the last image with circles superimposed
cv2.circle(
        rot, # image
        (img_info[-1].get('best').get('x'), img_info[-1].get('best').get('y')), # point (x,y)
        img_info[-1].get('best').get('r'), # radius
        (0,255.0), # colour
        2 # linethickness
        )
cv2.circle(
        rot,
        (img_info[-1].get('best').get('x'), img_info[-1].get('best').get('y')),
        2,
        (0,0.255),
        3
        )
cv2.imshow('circles', rot)

#fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
#video = cv2.VideoWriter(filename="out.mp4", fourcc, 25, (width, height), True)
#count = 0
#
#for name,data in img_info.items():
#    print(name, data)


#if __name__ == "__main__":
#    align_images_to_video(path, pattern)