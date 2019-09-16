#!/usr/bin/env python3
"""
Make the ICAPS timeline

"""
import matplotlib.pyplot as plt
# from matplotlib.patches import Ellipse
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import (TextArea, AnnotationBbox)

import pandas as pd

components = {}

end_mug = 364 # seconds
brown_time = 150 # seconds
agglomeration_time = 150 # seconds

relaxation_time = 5
analyse_injection_time = 0.5


tmin = -50
tmax = 450

#def add_component_time(name, time):
#    """
#    Add a new timeslot to the component
#    """
#    old_time = components.get(name).on_time
#    old_time.append(time)
#    components[name].on_time = old_time
#    return time[0] + time[1]

print(components)

class Component(object):
    def __init__(self, name, color, position):
        """
        Component definition
        """
        self.name = name
        self.color = color
        self.position = position
        self.dutycycle = []
        components[name] = self

    def add_time(self, timeslot):
        self.dutycycle.append(timeslot)
        return timeslot[0] + timeslot[1]

    def __str__(self):
        return self.name


class Camera(Component):
    def __init__(self, name, color, position, stream_fps=250, burst_fps=1000, download_fps=250, max_ram_images=24298, max_ssd_images=360672):
        super().__init__(name, color, position)
        self.stream_fps = stream_fps             # maximum framerate for streaming
        self.burst_fps  = burst_fps              # Time to download the whole memory
        self.download_fps = download_fps         # Rate at which images are downloaded from camera to HDD
        self.max_ram_images = max_ram_images     # Maximum amount of images which can be stored in volatile camera memory (used-up when fps > stream_fps)
        self.max_ssd_images = max_ssd_images     # Maximum amount of images which can be stored in total
        self.ram_images     = 0                  # Number of currently stored images in the volatile memory
        self.total_images   = 0
        self.fps = []

    def num_images(self, timeslot, fps=250):
        return timeslot[1]* fps

    def remaining_images(self):
        return self.stored_images

    def add_time(self, timeslot, fps=250):
        super().add_time(timeslot)
        num_images = self.num_images(timeslot, fps)
        if fps > self.stream_fps:
            self.ram_images += num_images
        self.total_images += num_images
        self.fps.append(fps)

def add_component(name, color, timeslot=None, ctype=Component):
    """
    construct a component and add it to L{components}
    """
    component = ctype(name, color, 0)
    if timeslot is not None:
        component.add_time(timeslot)
    components[name] = component

# name, color, [ (start, duration), (start, duration), ...]

#
add_component('observe hands-off',  'blueviolet')
# add_component('CMS levitate', 'mediumpurple')

add_component('CMS levitate',       'slateblue')
add_component('CMS squeeze',        'slateblue')
add_component('CMS scan -x',        'skyblue')
add_component('CMS scan +x',        'deepskyblue')
add_component('CMS scan -z',        'skyblue')
add_component('CMS scan +z',        'deepskyblue')

add_component('CMS E -z',           'steelblue')
add_component('CMS E +z',           'dodgerblue')

add_component('Scan cloud',         'salmon')
add_component('Scan agglomerate',   'palevioletred')

add_component('LDM illumination',   'yellow',      timeslot=(-5,tmax))
add_component('OOS illumination',   'peru',        timeslot=(-5,tmax))
add_component('LDM camera',         'olivedrab',   timeslot=(-5,tmax))
add_component('OOS camera',         'yellowgreen', timeslot=(-5,tmax))

add_component('analyse injection',  'lightgrey')
add_component('gas flow',           'lightgrey')
add_component('open shutter valve', 'dimgray')
add_component('injection piston',   'gray')
add_component('cogwheel',           'black')

#def OOS_mode(time, duration=0.1):
#    t = add_component_time('OOS illumination', (time, duration))
#    return t
#

def position_particle(time, duration=1):
    t = time
    t = components['CMS levitate'].add_time((time,duration))
    return t

def restore_cloud(time, duration=3):
    t = time
    t = components['CMS levitate'].add_time((time,duration))
    return t

def scan(time, direction='z'):
    t = time
    # center particle back and forth, look with LDM, LSU and sometimes also OOS
    t = components['CMS scan -' + direction].add_time((t,2))
    t = components['CMS scan +' + direction].add_time((t,4))
    t = components['CMS scan -' + direction].add_time((t,2))
    return t

def scan_cloud(time, duration=8, direction='z'):
    t = scan(time, direction=direction)
    components['Scan cloud'].add_time((time,t-time))
    return t

def scan_agglomerate(time):
    t = position_particle(time)
    t_scan = t
    t = scan(t)
    scan(t_scan, direction='x')
    components['Scan agglomerate'].add_time((t_scan, t-t_scan))
    # t = restore_cloud(t)
    return t

def step_view_agglomerate(time, n=1):
    t = time
    print("{:6.1f}: Starting cloud scan for particle(s).".format(t))
    t = scan_cloud(t,direction='x')
    for i in range(0,n):
        print("{:6.1f}: Positioning + scanning particle start.".format(t))
        t = position_particle(t, duration=1)
        t = scan_agglomerate(t)
        print("{:6.1f}: Positioning + scanning particle end.".format(t))
    return t

def step_brown(time):
    # 15s levitation (= keep cloud in centre, mostly undisturbed)
    t = time
    t = components['CMS levitate'].add_time((t, 13))
    # scan cloud in z-direction
    t = scan_cloud(t)
    return t

def scan_e(time, duration=2): # initial scan of the cloud
    t = time
    t = components['CMS E +z'].add_time((t, duration))
    t = components['CMS E -z'].add_time((t, duration))
    # Add 100ms of dead time to restore voltages to 0V
    t = components['observe hands-off'].add_time((t, 0.1))
    
    print("        Charge scan particle: {:4.1f}".format(t-time))
    return t

def step_squeeze(time):
    t = time
    # levitate / center cloud
    t = components['CMS levitate'].add_time((t, 3))
    # squeezing
    t = components['CMS squeeze'].add_time((t, 4))
    # levitate / center cloud
    t = components['CMS levitate'].add_time((t, 3))
    # squeezing
    t = components['CMS squeeze'].add_time((t, 4))
    # levitate / center cloud
    t = components['CMS levitate'].add_time((t, 3))
    print("        Step agglomerate: {:4.1f}".format(t-time))
    return t

#################################################
#### Define the actual sequences below here #####
#################################################
#
#
def phase_injection(time):
    t = time
    # An injection starts 5s before the actual injection with activation of stuff
    components['cogwheel'].add_time((t-5,8))
    components['open shutter valve'].add_time((-2,5))
    components['gas flow'].add_time((-2,5))
    t = components['injection piston'].add_time((t-1,4))
    
    t = components['analyse injection'].add_time((t,analyse_injection_time))
    # t = scan_e(t, duration=0.5)
    #    t = step_injection(t)
    
    print("{:6.1f}: Injection finished".format(t))
    return t
#
def phase_brown(time):
    # brownian motion first, Phase I
    print("{:6.1f}: Starting Brownian phase".format(time))   
    t0 = time
    t = scan_e(t0,duration=1)
    t = step_brown(t) # 1
    t = step_brown(t) # 2
    t = step_brown(t) # 3
    t = step_brown(t) # 4
    t = step_brown(t) # 5
    t = step_brown(t) # 6
    
    t = components['CMS levitate'].add_time((t,15))
    t = step_view_agglomerate(t)
    print("{:6.1f}: Ending Brownian phase.".format(t))

    return t

def phase_agglomerate(time):
    # electric measurement
    t = time
    print("{:6.1f}: Starting forced agglomeration phase".format(t))

    t = components['CMS levitate'].add_time((t,3))
    t = scan_e(t)
    t0 = t
    t = step_squeeze(t0)
    t = scan_cloud(t)
    t = step_squeeze(t)

    t = step_view_agglomerate(t)

    t = step_squeeze(t)
    t = scan_cloud(t)
    t = step_squeeze(t)
    t = scan_cloud(t)
    t = step_squeeze(t)
    
    t = step_view_agglomerate(t, n=3)

    # Final E-scan
    t = scan_e(t)

    print("{:6.1f}: Ending forced agglomeration phase.".format(t))
    return t

def phase_post_mug(time):
    t = components['observe hands-off'].add_time((time,end_mug-time))
    print("{:6.1f}: Starting undisturbed cloud expansion".format(time))
    print("{:6.1f}: End of µg, Shutting down of systems".format(t))
    return t


def convert_to_timeline(components):
    times_set = set()
    for item in components:
        for interval in components.get(item).dutycycle:
            times_set.add(interval[0])
            times_set.add(interval[0] + interval[1])
    times = list(times_set)
    times.sort()

    timeline = dict()
    timeline['time since µg'] = times
    for item in components:
        this_tl = ['' for x in times]
        for interval in components.get(item).dutycycle:
            t0 = times.index(interval[0])
            t1 = times.index(interval[0] + interval[1])
            this_tl[t0] = 'on'
            this_tl[t1] = 'off'
            timeline[item] = this_tl

    return timeline

def convert_pdframe_to_dict(pdframe):
    timeline = dict()
    for item in pdframe:
        this_list = list()
        times = pdframe[(pdframe[item] == 'on') | (pdframe[item] == 'off')]['time since µg']
        values = pdframe[(pdframe[item] == 'on') | (pdframe[item] == 'off')][item]
        for index, starttime in enumerate(times):
            if values[index] == 'on' and values[index+1] == 'off':
                this_list.append((starttime, times[index+1]-starttime))
        timeline[item] = this_list

    return timeline

def read_from_excel(filename='icaps_timeline.xlsx'):
    timeline = dict()
    pd_timeline = pd.read_excel(filename)
    return timeline

def write_to_excel(timeline):
    pd_timeline = pd.DataFrame.from_dict(timeline)
#    writer = pd.ExcelWriter('icaps_timeline.xlsx')
#    pd_timeline.to_excel(writer, sheet_name='Timeline')
#    writer.save()




total_time = phase_injection(0)
injection_time = total_time

# Do some initial measurements on the freshly-injected particles (part of injection)
#total_time = scan_e(total_time)
scan_e_time = total_time
total_time = components['observe hands-off'].add_time((total_time,relaxation_time))

# Brownian growth
start_brown = total_time

print("Pre-brown: ",total_time)
total_time = phase_brown(total_time)
print("Brown time: ",total_time)

# Use forced agglomeration to grow larger particles: Phase II
# Each takes 36 seconds: 12s electric analysis, 12s squeezing, 12s analysis
start_agglomerate = total_time
total_time = phase_agglomerate(total_time)
end_agglomerate = total_time

# continue until end: Phase III
total_time = phase_post_mug(total_time)
#
fig, ax = plt.subplots()
plt.setp(ax, zorder=0)
##ax.broken_barh([(110, 30), (150, 10)], (10, 9), facecolors='blue')
##ax.broken_barh([(10, 50), (100, 20), (130, 10)], (20, 9),
#               #facecolors=('red', 'yellow', 'green'))
## [(xstart, duration)], (ystart, height), facecolors=('color')
ticks = [0] * len(components)
#
with open('icaps_timeline.txt', 'w') as thefile:
    for index, item in enumerate(components, start = 1):
        dutycycle = components.get(item).dutycycle
        color = components.get(item).color
        ax.broken_barh(dutycycle, (index, 0.5), facecolors=color)
        ticks[index-1] = index
        thefile.write("%s: " % item)
        thefile.write("%s\n" % dutycycle)
    thefile.close()

timeline = convert_to_timeline(components)
write_to_excel(timeline)
#
ax.set_yticklabels(components)

ax.set_ylim(0, max(ticks)+1)
ax.set_xlim(tmin, tmax)
ax.set_xlabel('seconds since start of micro-g')
#
ax.set_yticks(ticks)
ax.grid(True)

ymax = len(components)

# Annotate 2nd injection
ax.annotate('optional 2nd,\ninjection starts here',
                  xy=(injection_time, ymax-2), xycoords='data',
                  xytext=(injection_time+20, ymax-2), textcoords='data',
                  size=8,
                  arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5))

ax.annotate('end of µg', (end_mug, ymax-2), xycoords='data',
            xytext=(end_mug+20,ymax-2), textcoords='data',
            size=8,
            arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5)),

# annotate different phases
ax.annotate('Brownian phase', (start_brown+(start_agglomerate - start_brown) / 2, ymax+0.5), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('Agglomeration phase', (start_agglomerate+(end_agglomerate - start_agglomerate) / 2, ymax+0.5), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('Scan', (end_agglomerate+(end_mug - end_agglomerate) / 2, ymax+0.5), textcoords='data',
            size=10, horizontalalignment='center')

# indicate exact times
uppery = 0.95
plt.axvline(x=injection_time, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
plt.axvline(x=start_agglomerate, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
plt.axvline(x=end_agglomerate, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
# annotate end of µg
plt.axvline(x=end_mug, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')

ax.annotate('{:3.0f}s'.format(injection_time), (injection_time+1, ymax), textcoords='data',
            size=10, horizontalalignment='left')
ax.annotate('{:3.0f}s'.format(start_agglomerate), (start_agglomerate, ymax), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('{:3.0f}s'.format(end_agglomerate), (end_agglomerate, ymax), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('{:3.0f}s'.format(end_mug), (end_mug, ymax), textcoords='data',
            size=10, horizontalalignment='center')

# Annotate scan for charges
rect2 = Rectangle((tmin+25,0.2),150,1.5,
                  fill=True, alpha=1, zorder=1,
                  facecolor='white',linewidth=1.5,linestyle='-',edgecolor='black')

# Annotate the 1st position with a text box ('Test 1')
text_scandir = TextArea("Adjust x and z scan speed such that agglomerates\n are scanned in the viewing direction of the LDM", minimumdescent=False)
ab = AnnotationBbox(text_scandir, (tmin+60, 2.7),
                    xybox=(15, 11.5), # center of text box in data coordinates
                    xycoords='data',
                    boxcoords="data"
                    )
ax.add_artist(ab)


text_scandir = TextArea("Note:\nSequence assumes that\n the LDM camera cannot\n see the OOS light and\n vice versa (e.g. that\n colour filters are used).\nCMS levitate includes\nkeeping cloud in centre.", minimumdescent=False)
ab2 = AnnotationBbox(text_scandir, (422, 1),
                    xybox=(417, 1.7), # center of text box in data coordinates
                    xycoords='data',
                    boxcoords="data"
                    )
ax.add_artist(ab2)


plt.subplots_adjust(left=0.15)
plt.show()
