#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 12:37:34 2018

@author: ingo
"""

import cv2
import numpy as np

def detect_circles(img, relative_radius_percent=20, gradient=10, threshold=40, minRadius=None, maxRadius=None):
    try:
        height, width, channels = img.shape
    except AttributeError:
        return None

    radius = max([height, width]) / 2
    if minRadius == None:
        minRadius = int(radius * (100-relative_radius_percent)/100)
    if maxRadius == None:
        maxRadius = int(radius * (100+relative_radius_percent)/100)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, radius,
                  param1=gradient,
                  param2=threshold,
                  minRadius=minRadius,
                  maxRadius=maxRadius,
                  )

    return circles

if __name__ == "__main__":
    img = cv2.imread('/home/ingo/pytools/examples/sun_example2.jpg',cv2.IMREAD_COLOR)
    circles = detect_circles(img)

    print(circles)
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
        cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

    print("Press any key in the image window to continue")
    cv2.imshow('circles', img)

    k = cv2.waitKey(0)
    if k == 27:
        cv2.destroyAllWindows()