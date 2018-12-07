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

#fourcc = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
#video = cv2.VideoWriter(filename="out.mp4", fourcc, 25, (width, height), True)
#count = 0

defx = None
defy = None

img_info = []
for file in files[0:50]:
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
    best,circles = detect_circles(rot,similar={'bestx':width, 'besty':height})
    if circles is None:
        print("No circle found in {}".format(file))
        continue
    img_info.append({
            'name':file,
            'width': width,
            'height': height,
            'channels': channels,
            'circles': circles,
            'rotate':rotate,
            'best': best,
            })

    # if it is the first image, we define the centere and align everything
    #     else according to this
    if defx == None:
        defx = best.get('x')
        defy = best.get('y')
        dx = 0
        dy = 0
        print("Setting default x and y values for centre")
    else:
        dx = defx - best.get('x')
        dy = defy - best.get('y')

    moveM = np.float32([[1,0,-dy],[0,1,-dx]])
    moved = cv2.warpAffine(rot, moveM, (img_info[-1].get('width'),img_info[-1].get('height')))

    print(dx,dy)
    cv2.imshow('wackelfrei', moved)
    cv2.imshow('wackelnd', rot)
    cv2.waitKey(1)

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


#if __name__ == "__main__":
#    align_images_to_video(path, pattern)