#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 12:57:52 2018

@author: ingo
"""
import numpy as np
import glob, os, subprocess

from math import sqrt, pi

import matplotlib.pyplot as plt
# Use PIL to save some image metadata
from PIL import Image
from PIL import PngImagePlugin

from BNE.bne_read_ods_ingo import bne_read_ods_ingo
from BNE.bne_read_ods_fabian import bne_read_ods_fabian
from BNE.bne_read_ods_yamada import bne_read_ods_yamada

from BNE.single_stage_programme import stage_programme_names, single_stage_programme
from BNE.bne_config import bne_config
from tools.version_info import get_hg_version, get_git_version



############################### main programme ###########################

experiments = []

def pretty_print_exp(e):
    """
    Print the essential parts for an experiment
    """
    assert (e is not None)

    s = "{:4}-{:6}: {:4}g x {:4}".format(e.get('exp_id'),e.get('origin'),e.get('ambient_t'),e.get('rel_excitation'))
    s += "\n    A={} @ {}Hz; vrise={}".format(e.get('amplitude'),e.get('frequency'),e.get('vmax'))
    print(s)

def get_rel_excitation(e):
    """
    Calculate the relative excitation, if it hasn't been defined so far
    """
    assert (e is not None)

    gamma = e.get('rel_excitation')

    if gamma is None:
        try:
            amp = e.get('amplitude')
            f = e.get('frequency')
            g = e.get('ambient_g') * bne_config.get('g')
            gamma = amp + (2 * pi * f)**2 / g
        except:
            gamma = np.NaN

    return gamma

def get_vstar(e):
    """
    Calculate the maximum dimensionless velocity
    vstar = vmax / sqrt (ambient_g * bead_diameter)
    """
    assert (e is not None)

    vmax = e.get('vmax')
    if vmax is None:
        vmax = e.get('v1')

    try:
        g = e.get('ambient_g') * bne_config.get('g')
        d = e.get('bead_radius') * 2
        vstar = vmax / sqrt(g * d)
    except:
        vstar = np.NaN

    return vstar

def get_shaking(e):
    """
    Calculate the shaking
    S = (v_vib / v_grav)^2 = gamma * amp / bead_diameter
    """
    assert (e is not None)

    try:
        amp = e.get('amplitude')
        f   = e.get('frequency')
        g   = e.get('ambient_g') * bne_config.get('g')
        d   = e.get('bead_radius') * 2
        S = (2 * pi * amp * f)**2 / (g * d)
    except:
        S = np.NaN

    # DEBUG
    # print("{}-{}: A={}, f={}, g={}, r={} --> S={}".format(e.get('exp_id'),e.get('origin'), amp, f, g, r, S))
    return S

def get_L(e):
    """
    Calculate the dimensionless dimension
    """
    assert (e is not None)

    try:
        R = e.get('container_radius')
        H = e.get('fill_height')
        d = e.get('bead_radius') * 2
        L = sqrt(R * H) / d
    except:
        L = np.NaN

    return L

def add_image_metadata(f, metadata=None):
    # I don't know of a way using matplotlib, but you can add metadata to png's with PIL:
    im = Image.open(f)
    meta = PngImagePlugin.PngInfo()

    for key,value in metadata.items():
        meta.add_text(key, value)
    im.save(f, "png", pnginfo=meta)


def write_diff(path):
    with open(os.path.join(path,"code.diff"), "w") as f:
        subprocess.run(["git", "-C", bne_config.get('code_path'), "diff", "HEAD"],stdout=f, universal_newlines=True)
    with open(os.path.join(path,"data.diff"), "w") as f:
        subprocess.run(["hg", "-R", bne_config.get('project_path'), "diff"],stdout=f, universal_newlines=True)


def bne_model_powerlaw(x, A):
    pass

######################################################################
#### Main programme ##################################################
######################################################################
def main():
#    rawdata_ingo = bne_read_ods_ingo()
#    rawdata_fabian = bne_read_ods_fabian()
#    rawdata_yamada = bne_read_ods_yamada()
#
#    exps_ingo = rawdata_ingo.get_list_of_dicts()
#    exps_fabian = rawdata_fabian.get_list_of_dicts()
#    exps_yamada = rawdata_yamada.get_list_of_dicts()
#
#    print("Number of experiments by Ingo: {}".format(len(exps_ingo)))
#    print("Number of experiments by Fabian: {}".format(len(exps_fabian)))
#    print("Number of experiments by Yamada et al: {}".format(len(exps_yamada)))
#    return exps_ingo + exps_fabian + exps_yamada
#

    ######################################################################
    #### Get the stage programmes#########################################
    ######################################################################

    stage_programme_names_ingo = stage_programme_names()
    stage_programme_names_ingo.read_file()
    programmes_ingo = stage_programme_names_ingo.get_programme_info()

    programme_info = []

    for i,name in enumerate(programmes_ingo['name']):
        filename_pattern = programmes_ingo['filenames'][i]
        duration_str = programmes_ingo['duration'][i]

        if type(duration_str == str):
            try:
                duration = float(duration_str.replace(",",".").replace("?",""))
            except:
                duration = None
        else:
            duration = float(duration_str)

        try:
            acc_rise_times_str = programmes_ingo.get('acc_rise_times')[i]
            try:
                acc_rise_times = [int(t) for t in acc_rise_times_str]
            except (ValueError, TypeError) as error:
                acc_rise_times = None
        except KeyError:
            acc_rise_times = None

        filenames = glob.glob(bne_config.get('project_path') + bne_config.get('sensor_path') + filename_pattern)
        success = {}
        if len(filenames) == 0:
            print("No files found for {}, matching {}".format(name, filename_pattern))
            continue

        try:
            prg_info = single_stage_programme(name, filenames[0], "")
            success['init'] = True
        except:
            success['init'] = False
        try:
            prg_info.read_by_filename()
            success['reading'] = True
        except:
            success['reading'] = False
        try:
            prg_info.extract_data(None, duration, acc_rise_times)
            success['extraction'] = True
        except:
            success['extraction'] = False

        prg_info.ambient_g = programmes_ingo['ambient_g'][i]
        prg_info.relative_excitation = programmes_ingo['relative_excitation'][i]
        prg_info.acc_rise_times = acc_rise_times
        prg_info.duration = duration
        prg_info.amplitude = bne_config.get('amplitude_ingo')
        if prg_info.frequency is None and duration is not None and acc_rise_times is not None:
            prg_info.frequency = 5000 * duration / (acc_rise_times[1] - acc_rise_times[0])

        # print("{:80s}: Init: {:3}, Reading: {:3}, Data extraction: {:3} ({}s)".format(filenames[0],success['init'], success['reading'], success['extraction'], duration))

        programme_info.append(prg_info)
        print(prg_info)



    rawdata_ingo = bne_read_ods_ingo()
    rawdata_fabian = bne_read_ods_fabian()
    rawdata_yamada = bne_read_ods_yamada()

    exps_ingo = rawdata_ingo.get_list_of_dicts()
    exps_fabian = rawdata_fabian.get_list_of_dicts()
    exps_yamada = rawdata_yamada.get_list_of_dicts()

    exps = exps_ingo + exps_fabian + exps_yamada

    # Get all possible origins
    origins = set([e.get('origin') for e in exps])
    n_origins = len(origins)

    symbols = ['+', 'x', '*', 's', 'D', '3', '4']

    # Get the number, sorted by origin
    for o in origins:
        print("Number of experiments by {}: {}".format(o, len([e for e in exps if e.get('origin') == o])))

    # Add those parameters which we need for all in a uniform way
    for e in exps:
        gamma = get_rel_excitation(e)
        e['rel_excitation'] = gamma

        vstar = get_vstar(e)
        e['vstar'] = vstar

        S = get_shaking(e)
        e['S'] = S

        L = get_L(e)
        e['L'] = L

    # Create directory for saved plots
    codeversion, code_modified = get_git_version()
    dataversion, data_modified = get_hg_version(bne_config.get('project_path'))
    figure_path = bne_config.get('project_path') + bne_config.get('plot_path') + codeversion + '/'
    if not os.path.exists(figure_path):
        os.makedirs(figure_path)
    write_diff(figure_path)
    png_metadata = {
            'Author': 'TU Braunschweig, Ingo von Borstel',
            'Code version': codeversion,
            'Data version': dataversion,
            'Software': "Brazil nut experiments analysis",
            }

    # Show coverage of parameter range in relative excitation and ambient gravity
    fig, ax = plt.subplots(1,1,num='rel. excitation over ambient g')
    filename = figure_path + 'bne_ambientg_relExcitation.png'
    ax.plot([e.get('ambient_g') for e in exps], [e.get('rel_excitation') for e in exps], '.', color='white')
    plt.xlabel('ambient gravity [g]')
    plt.ylabel('relative excitation $\Gamma$')
    for o,s in zip(origins, symbols):
        es = [e for e in exps if e.get('origin') == o]
        ax.plot([e.get('ambient_g') for e in es], [e.get('rel_excitation') for e in es], s, label=o)
    legend = ax.legend(loc='upper right')
    plt.show()
    plt.savefig(filename)
    add_image_metadata(filename, metadata=png_metadata)

    # Show coverage of parameter range in relative excitation and frequency
    fig, ax = plt.subplots(1,1,num='rel. excitation over frequency')
    filename = figure_path + 'bne_frequency_relExcitation.png'
    ax.plot([e.get('frequency') for e in exps], [e.get('rel_excitation') for e in exps], '.', color='white')
    plt.xlabel('frequency [Hz]')
    plt.ylabel('relative excitation $\Gamma$')
    for o,s in zip(origins, symbols):
        es = [e for e in exps if e.get('origin') == o]
        ax.plot([e.get('frequency') for e in es], [e.get('rel_excitation') for e in es], s, label=o)
    legend = ax.legend(loc='lower right')
    plt.show()
    plt.savefig(filename)
    add_image_metadata(filename, metadata=png_metadata)

    fig, ax = plt.subplots(1,1,num='rise velocity over gamma')
    filename = figure_path + 'bne_relExcitation_vstar.png'
    ax.loglog([e.get('rel_excitation') for e in exps], [e.get('vstar') for e in exps], '.', color='white')
    plt.xlabel('relative excitation $\Gamma$ [1]')
    plt.ylabel('rise velocity v* [1]')
    for o,s in zip(origins, symbols):
        es = [e for e in exps if e.get('origin') == o]
        ax.loglog([e.get('rel_excitation') for e in es], [e.get('vstar') for e in es], s, label=o)
    legend = ax.legend(loc='lower right')
    plt.show()
    plt.savefig(filename)
    add_image_metadata(filename, metadata=png_metadata)

    fig, ax = plt.subplots(1,1,num='rise velocity over relative shaking energy')
    filename = figure_path + 'bne_S_vstar.png'
    ax.loglog([e.get('S') for e in exps], [e.get('vstar') for e in exps], '.', color='white')
    plt.xlabel('rel. shaking energy S [1]')
    plt.ylabel('rise velocity v* [1]')
    for o,s in zip(origins, symbols):
        es = [e for e in exps if e.get('origin') == o]
        ax.loglog([e.get('S') for e in es], [e.get('vstar') for e in es], s, label=o)
    legend = ax.legend(loc='lower right')
    plt.show()
    plt.savefig(filename)
    add_image_metadata(filename, metadata=png_metadata)

    exi = exps
    fig, ax = plt.subplots(1,1,num='rise velocity over excitation')
    filename = figure_path + 'bne_relExcitation_vmax.png'
    ax.loglog([e.get('rel_excitation')-1 for e in exi], [e.get('v1') for e in exi], '.', color='white')
    plt.xlabel('rel. excitation -1 [g]')
    plt.ylabel('rise velocity mm/s')
    glevels = set([e.get('ambient_g') for e in exi])
    for g,s in zip(glevels,symbols):
        es = [e for e in exi if e.get('ambient_g') == g]
        ax.loglog([e.get('rel_excitation')-1 for e in es], [e.get('v1') for e in es], s, label=g)
        print("g={}: ({:3} exps, {:3}x v1 defined)".format(g, len(es), len(es)-[e.get('v1') for e in es].count(np.NaN)))
    legend = ax.legend(loc='lower right')
    plt.show()
    plt.savefig(filename, metadata=png_metadata)
#    add_image_metadata(filename, metadata=png_metadata)

    return exps

if __name__ == "__main__":
    exps = main()