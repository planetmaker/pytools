#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 10:31:21 2018

https://alexanderpacha.com/2018/01/29/aligning-images-an-engineers-solution/

@author: ingo
"""

from cv2 import cv2, countNonZero, cvtColor

im1 = cv2.imread(path_to_desired_image)
im2 = cv2.imread(path_to_image_to_warp)

warp_mode = cv2.MOTION_AFFINE
warp_matrix = np.eye(2, 3, dtype=np.float32)

# Specify the number of iterations.
number_of_iterations = 100

# Specify the threshold of the increment in the correlation
# coefficient between two iterations
termination_eps = 1e-7

criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
            number_of_iterations, termination_eps)

# Run the ECC algorithm. The results are stored in warp_matrix.
(cc, warp_matrix) = cv2.findTransformECC(im1, im2, warp_matrix,
                                         warp_mode, criteria)

# Lastly, one “only” needs to warp the image with the found affine transformation:

aligned_image = cv2.warpAffine(
                          unaligned_image,
                          warp_matrix,
                          (sz[1], sz[0]),
                          flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                          borderMode=cv2.BORDER_CONSTANT,
                          borderValue=0)

cv2.imwrite(destination_path, aligned_image)