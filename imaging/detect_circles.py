#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 12:37:34 2018

@author: ingo
"""
#
#import cv2
#import numpy as np
#
#"""
#params = dict(dp=1,
#              minDist=1,
#              circles=None,
#              param1=300,
#              param2=290,
#              minRadius=1,
#              maxRadius=100)
#"""
#
#img = np.ones((200,250,3), dtype=np.uint8)
#for i in range(50, 80, 1):
#    for j in range(40, 70, 1):
#        img[i][j]*=200
#
#cv2.circle(img, (120,120), 20, (100,200,80), -1)
#
#
#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#canny = cv2.Canny(gray, 200, 300)
#
#cv2.imshow('shjkgdh', canny)
#gray = cv2.medianBlur(gray, 5)
#circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
#              param1=100,
#              param2=30,
#              minRadius=0,
#              maxRadius=0)
#
#if circles != None:
#    print(circles)
#
#circles = np.uint16(np.around(circles))
#for i in circles[0,:]:
#    cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
#    cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
#
#cv2.imshow('circles', img)
#k = cv2.waitKey(0)
#if k == 27:
#    cv2.destroyAllWindows()

import cv2
import numpy as np

img = cv2.imread('/home/ingo/pytools/sun_example2.jpg',cv2.IMREAD_COLOR)

height, width, channels = img.shape

sun_radius = max([height, width]) / 2
sun_radius_min = sun_radius * 0.8
sun_radius_max = sun_radius * 1.2

#img = np.ones((200,250,3), dtype=np.uint8)
#for i in range(50, 80, 1):
#    for j in range(40, 70, 1):
#        img[i][j]*=200

#cv2.circle(img, (120,120), 20, (100,200,80), -1)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, sun_radius,
              param1=50,
              param2=40,
              minRadius=sun_radius_min,
              maxRadius=sun_radius_max)

print(circles)
circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
    cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

cv2.imshow('circles', img)

k = cv2.waitKey(0)
if k == 27:
    cv2.destroyAllWindows()