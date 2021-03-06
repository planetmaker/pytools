#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 10:26:00 2018

Aligning images based on similarity of features
https://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/

@author: ingo
"""

import cv2
import numpy as np

if __name__ == '__main__':

    # Read 8-bit color image.
    # This is an image in which the three channels are
    # concatenated vertically.

    im =  cv2.imread("images/emir.jpg", cv2.IMREAD_GRAYSCALE);

    # Find the width and height of the color image
    sz = im.shape
    print sz
    height = int(sz[0] / 3);
    width = sz[1]

    # Extract the three channels from the gray scale image
    # and merge the three channels into one color image
    im_color = np.zeros((height,width,3), dtype=np.uint8 )
    for i in xrange(0,3) :
        im_color[:,:,i] = im[ i * height:(i+1) * height,:]

    # Allocate space for aligned image
    im_aligned = np.zeros((height,width,3), dtype=np.uint8 )

    # The blue and green channels will be aligned to the red channel.
    # So copy the red channel
    im_aligned[:,:,2] = im_color[:,:,2]

    # Define motion model
    warp_mode = cv2.MOTION_HOMOGRAPHY

    # Set the warp matrix to identity.
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
            warp_matrix = np.eye(3, 3, dtype=np.float32)
    else :
            warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Set the stopping criteria for the algorithm.
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 5000,  1e-10)

    # Warp the blue and green channels to the red channel
    for i in xrange(0,2) :
        (cc, warp_matrix) = cv2.findTransformECC (get_gradient(im_color[:,:,2]), get_gradient(im_color[:,:,i]),warp_matrix, warp_mode, criteria)

        if warp_mode == cv2.MOTION_HOMOGRAPHY :
            # Use Perspective warp when the transformation is a Homography
            im_aligned[:,:,i] = cv2.warpPerspective (im_color[:,:,i], warp_matrix, (width,height), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        else :
            # Use Affine warp when the transformation is not a Homography
            im_aligned[:,:,i] = cv2.warpAffine(im_color[:,:,i], warp_matrix, (width, height), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
        print warp_matrix

    # Show final output
    cv2.imshow("Color Image", im_color)
    cv2.imshow("Aligned Image", im_aligned)
    cv2.waitKey(0)