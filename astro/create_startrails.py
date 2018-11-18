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

import sys

# Files to use

def process_raw(raw):
    ret = raw.postprocess(
#            output_color=rawpy.ColorSpace.raw, 
            output_color=rawpy.ColorSpace.sRGB,
            gamma = (5.222, 1.5), 
            output_bps = 16,
            use_camera_wb=False,
            user_wb=[0.7, 0.5, 1, 0.5],
            no_auto_bright=True,
            bright=0.1,
            user_sat=0,
            demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
            )

    return ret.astype('float32')

def get_files(path, first_cr2_filename, last_cr2_filename):
    allfiles = sorted([f for f in listdir(path) if isfile(join(path, f))])

    assert first_cr2_filename in allfiles, "{} not in directory".format(first_cr2_filename)    
    assert last_cr2_filename in allfiles, "{} not in directory".format(last_cr2_filename)
   
    index_first = [i for i, f in enumerate(allfiles) if f == first_cr2_filename][0]
    index_last  = [i for i, f in enumerate(allfiles) if f == last_cr2_filename][0]

    cr2_filenames = allfiles[index_first:index_last]
    return cr2_filenames

def create_startrail_array(
        cr2_path, 
        cr2_filenames, 
        noise_supp=758,
        log_highlight_percentile=96,
        linear_highlight_percentile=97
        ):
    # Initiallize it with the first image
    with rawpy.imread(cr2_path + cr2_filenames[0]) as raw:
        img = process_raw(raw)
        current = img
        
    # Iterate through all filenames
    for file in cr2_filenames[1:]:
        with rawpy.imread(cr2_path + file) as raw:
            img = process_raw(raw)
            
        img = np.maximum(current, img)
        current = img
    
    # Logarithmic brightness
    logimg = np.log10(img+noise_supp+1)-np.log10(noise_supp)
    maxlog = np.percentile(logimg, log_highlight_percentile)
    logimg = np.clip(logimg * 255 / maxlog, 0, 255).astype('uint8')
    
    # normal brightness
    maximg = np.percentile(img, linear_highlight_percentile)
    img = np.clip(img * 255 / maximg, 0, 255).astype('uint8')

    return img, logimg

def display_startrail_image(img):
    disp = Image.fromarray(img, 'RGB')
    disp.show()
    
def save_startrail_image(img, filename):
    imageio.imsave(filename, img)
    

if __name__ == '__main__':
    
    try:
        cr2_path = sys.argv[1]
    except:
        cr2_path = "/home/planetmaker/Bilder/2017/2017-03-22/"
    
    try:
        first_cr2_filename = sys.argv[2]
    except:
        first_cr2_filename = "IVB_7266.CR2"
        
    try:
        last_cr2_filename = sys.argv[3]
    except:
        last_cr2_filename = "IVB_7554.CR2"
    
#    try:
#        first_cr2_filename = sys.argv[2]
#    except:
#        first_cr2_filename = "IVB_7327.CR2"
#        
#    try:
#        last_cr2_filename = sys.argv[3]
#    except:
#        last_cr2_filename = "IVB_7337.CR2"

    try:
        output_jpg_linear = sys.argv[4]
    except:
        output_jpg_linear = "/home/planetmaker/Bilder/test_linear.jpeg"
        
    try:
        output_jpg_log = sys.argv[5]
    except:
        output_jpg_log = "/home/planetmaker/Bilder/test_log.jpeg"

#    first_cr2_filename = "IVB_7327.CR2"
#    last_cr2_filename = "IVB_7337.CR2"
    
#    first_cr2_filename = "IVB_7266.CR2"
#    last_cr2_filename = "IVB_7554.CR2"
    
    # Output filename:
#    jpg_filename = "/home/planetmaker/Bilder/test.jpeg"
    
    cr2_filenames = get_files(cr2_path, first_cr2_filename, last_cr2_filename)
    
    assert len(cr2_filenames) > 0, "There must be at least one valid image filename given"
    
    img, logimg = create_startrail_array(
            cr2_path,
            cr2_filenames,
            )
    
    display_startrail_image(logimg)
#    display_startrail_image(img)
    
    save_startrail_image(logimg, output_jpg_log)
    save_startrail_image(img, output_jpg_linear)
