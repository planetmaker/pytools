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

cr2_path = "/home/planetmaker/Bilder/2017/2017-03-22/"

first_cr2_filename = "IVB_7552.CR2"
last_cr2_filename = "IVB_7554.CR2"

#first_cr2_filename = "IVB_7266.CR2"
#last_cr2_filename = "IVB_7554.CR2"

jpg_filename = "/home/planetmaker/Bilder/test.jpeg"

def process(raw):
    ret = raw.postprocess(
            output_color=rawpy.ColorSpace.raw, 
            gamma = (1,1), 
            output_bps = 16,
            use_camera_wb=False,
            user_wb=[2.0, 1.0, 2.0, 1.0],
            no_auto_bright=True,
            bright=1.0,
            demosaic_algorithm=rawpy.DemosaicAlgorithm.LINEAR,
            )

    return ret

from os import listdir
from os.path import isfile, join
onlyfiles = sorted([f for f in listdir(cr2_path) if isfile(join(cr2_path, f))])

index_first = [i for i, f in enumerate(onlyfiles) if f == first_cr2_filename][0]
index_last  = [i for i, f in enumerate(onlyfiles) if f == last_cr2_filename][0]

cr2_filenames = onlyfiles[index_first:index_last]

with rawpy.imread(cr2_path + cr2_filenames[0]) as raw:
    img = process(raw)
    current = img
    
for file in cr2_filenames[1:]:
    with rawpy.imread(cr2_path + file) as raw:
        img = process(raw)
        
    img = np.maximum(current, img)
    current = img

imageio.imsave(jpg_filename, img)

disp = Image.fromarray((img / 255).astype('uint8'), 'RGB')
disp.show()