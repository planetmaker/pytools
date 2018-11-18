#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 22:00:42 2018

@author: planetmaker
"""

import rawpy
import imageio
import numpy as np
from PIL import Image

from os import listdir
from os.path import isfile, join

# Files to use
cr2_path = "/home/planetmaker/Bilder/2017/2017-03-22/"

#first_cr2_filename = "IVB_7327.CR2"
#last_cr2_filename = "IVB_7337.CR2"

first_cr2_filename = "IVB_7266.CR2"
last_cr2_filename = "IVB_7554.CR2"

# Output filename:
jpg_filename = "/home/planetmaker/Bilder/test.jpeg"

def process(raw):
    ret = raw.postprocess(
#            output_color=rawpy.ColorSpace.raw, 
            output_color=rawpy.ColorSpace.sRGB,
            gamma = (2.222, 4.5), 
            output_bps = 16,
            use_camera_wb=False,
            user_wb=[0.75, 0.5, 1, 0.5],
            no_auto_bright=True,
            bright=0.1,
            user_sat=0,
            demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
            )

    return ret.astype('float32')

allfiles = sorted([f for f in listdir(cr2_path) if isfile(join(cr2_path, f))])

index_first = [i for i, f in enumerate(allfiles) if f == first_cr2_filename][0]
index_last  = [i for i, f in enumerate(allfiles) if f == last_cr2_filename][0]

cr2_filenames = allfiles[index_first:index_last]

with rawpy.imread(cr2_path + cr2_filenames[0]) as raw:
    img = process(raw)
    current = img
    
for file in cr2_filenames[1:]:
    with rawpy.imread(cr2_path + file) as raw:
        img = process(raw)
        
    img = np.maximum(current, img)
    current = img

noise_supp = 5000
logimg = np.log10(img+noise_supp+1)-np.log10(noise_supp)
maxlog = np.percentile(logimg, 97)
logimg = np.clip(logimg * 255 / maxlog, 0, 255).astype('uint8')
disp2 = Image.fromarray(logimg, 'RGB')
disp2.show()

maximg = np.percentile(img, 97)
img = np.clip(img * 255 / maximg, 0, 255).astype('uint8')
#disp = Image.fromarray(img, 'RGB')
#disp.show()

imageio.imsave(jpg_filename, logimg)

