#!/usr/bin/env python3
"""
Make the ICAPS timeline
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

components = {}

def add_component_time(name, time):
    """
    Add a new timeslot to the component
    """
    old_time = components.get(name).on_time
    old_time.append(time)
    components[name].on_time = old_time
    return time[0] + time[1]

class Component(object):
    def __init__(self, name, color, position, on_time):
        """
        Component definition
        """
        self.name = name
        self.color = color
        self.position = position
        self.on_time = on_time

    def add_time(self, time):
        self.on_time.append(time)
        return time[0] + time[1]

    def __str__(self):
        return self.name


#class Camera(Component):
#    def __init__(self, name, color, position, on_time):
#        __super__.init(self, name, color, position, on_time)
#        self.max_recording_time = 10 # Set to the actual value in seconds
#        self.download_time      = 20 # Time to download the whole memory
#        self.remaining_rec_time = self.max_recording_time
#
#    def add_time(self, time):
#        __super__.add_time(self, time)
#        self.remaining_rec_time -= time[1]


def add_component(name, color, on_time):
    """
    construct a component and add it to L{components}
    """
    component = Component(name, color, 0, on_time)
    components[name] = component

# name, color, [ (start, duration), (start, duration), ...]

add_component('restore cloud',      'mediumpurple',   [])
add_component('center particle',    'mediumpurple',   [])
add_component('adjust CMS',         'darkorchid',     [])
add_component('measure cloud v',    'blueviolet',     [])
add_component('CMS levitate',       'slateblue',      [])
add_component('CMS squeeze',        'slateblue',      [])

add_component('OOS illumination',   'peru',           [])
add_component('LDM illumination',   'yellow',         [])

add_component('CMS scan -x 1mm/s',  'skyblue',        [])
add_component('CMS scan +x 1mm/s',  'deepskyblue',    [])
add_component('CMS E -x',           'aqua',           [])
add_component('CMS E +x',           'aquamarine',     [])
add_component('CMS E -y',           'aqua',           [])
add_component('CMS E +y',           'aquamarine',     [])
add_component('CMS E -z',           'aqua',           [])
add_component('CMS E +z',           'aquamarine',     [])

add_component('scan particle',      'palevioletred',  [])
add_component('Forced agglom.',     'lightpink',      [])
add_component('Brownian motion',    'lightpink',      [])

add_component('LDM high-speed',     'olive',          [])
add_component('LDM streaming',      'darkolivegreen', [])
add_component('LDM camera',         'olivedrab',      [(-5,600)])
add_component('OOS camera',         'yellowgreen',    [(-5,600)])

add_component('analyse injection',  'lightgrey',      [])
add_component('open shutter valve', 'dimgray',        [])
add_component('injection piston',   'gray',           [])
add_component('cogwheel',           'black',          [])

max_memory = 8*1024*1024*1024 / 1920/1280 *8/12
f_streaming = 185

def LDM_highspeed(time, duration=0.02):
    t = time
    t = add_component_time('LDM illumination', (t, duration))
    return t

def LDM_stream(time, duration=0.1):
    t = time
    t = add_component_time('LDM illumination', (t, duration))
    return t

def OOSLDM_mixed_mode(time, duration=0.1):
    t = time
    n = round(duration / 0.04)
    unused_time = (duration+0.0005) % 0.04
    if unused_time > 0.001:
        print("No multiple of 40ms defined as mixed mode sequence! Unused time: " + str(unused_time))
    # Alternatingly use OOS and LDM
    for count in range(0, int(n)):
        startt = t
        t = add_component_time('LDM illumination', (t,0.02))
        add_component_time('LDM streaming',    (startt, 0.02))
        t = add_component_time('OOS illumination', (t,0.02))
    return t

def adjust_CMS(time):
    t = time
    t = add_component_time('measure cloud v', (t,1))
    t = add_component_time('adjust CMS', (t,1))
    OOSLDM_mixed_mode(time,t-time)
    return t
def position_particle(time):
    t = time
    t = OOSLDM_mixed_mode(t,3)
    add_component_time('center particle',(time,t-time))
    return t
def restore_cloud(time):
    t = time
    t = OOSLDM_mixed_mode(t,3)
    add_component_time('restore cloud',(time,t-time))
    return t

def scan_cloud(time):
    t = time
    # center particle back and forth, look with LDM, LSU and sometimes also OOS
    t = add_component_time('CMS scan +x 1mm/s', (t,3))
    t = add_component_time('CMS scan -x 1mm/s', (t,6))
    t = add_component_time('CMS scan +x 1mm/s', (t,3))
    LDM_highspeed(time,t-time)
    return t
def scan(time):
    t = time
    t = scan_cloud(t)
    return t

def loop_brown(time, test=False):
    # observe 10s
    t = time
    t = LDM_highspeed(t,1) # observe unperturbed 1s
    t_start_levitate = t
    t = OOSLDM_mixed_mode(t,7) # observe unperturbed, but levitate
    add_component_time('CMS levitate', (time,t-t_start_levitate))
    # t = adjust_CMS(t)
    t = scan_cloud(t)
    add_component_time('Brownian motion',(time,t-time))
    return t

def largest_particle(time):
    t = time
    t = adjust_CMS(t)    # 2s
    t = position_particle(t) # 3s
    scan_t = t
    t = scan(t) # 12s
    add_component_time('scan particle', (scan_t,t-scan_t))
    t = restore_cloud(t) # 3
    print("{:6.1f}: Largest particle finished in {:4.1f}s.".format(t,t-time))
    return t

def scan_e(time): # initial scan of the cloud
    t = time
    t = add_component_time('CMS E +x', (t, 0.5))
    t = add_component_time('CMS E -x', (t, 0.5))
    t = add_component_time('CMS E +y', (t, 0.5))
    t = add_component_time('CMS E -y', (t, 0.5))
    t = add_component_time('CMS E +z', (t, 0.5))
    t = add_component_time('CMS E -z', (t, 0.5))
    LDM_highspeed(time, t-time)
    print("        Charge scan particle: {:4.1f}".format(t-time))
    return t

def loop_agglomerate(time):
    t = time
    # electric measurement
    t = add_component_time('CMS E +x', (t,3))
    t = add_component_time('CMS E -x', (t,6))
    t = add_component_time('CMS E +x', (t,3))
    OOSLDM_mixed_mode(time,t-time)
    # squeezing
    t = add_component_time('CMS squeeze', (t, 15))
    OOSLDM_mixed_mode(t-15,15)
    # scan
    t = scan(t)
    add_component_time('Forced agglom.',(time,t-time))
    print("        Loop agglomerate: {:4.1f}".format(t-time))
    return t

################################################
### Define the actual sequences below here #####
################################################


def phase_injection(time):
    t = time
    # First 22 seconds are injection. That's directly defined above in the item definitions
    add_component_time('cogwheel', (-30,60))
    # add_component_time('LSU illumination', (-20,5))

    add_component_time('injection piston', (-1,6))
    add_component_time('open shutter valve', (0,5))
    t = add_component_time('analyse injection',    (5,20))
    OOSLDM_mixed_mode(-1,t+1)

    # possible re-injection
    add_component_time('open shutter valve', (15,5))
    add_component_time('injection piston', (14,6))
    print("{:6.1f}: Injection finished".format(t))
    return t

def phase_brown(time, duration=202-22):
    # brownian motion first, Phase I
    # Each takes 24 seconds: 2s CMS adjustment, 10s nothing, 12s analysis
    t0 = time
    t = loop_brown(t0)
    loop_duration = t - t0
    n_loops, t_remain = divmod(duration, loop_duration)
    n_loops = int(n_loops)
    print("        Executing {} Brown loops of {:4.1f}s length each. {:4.1f}s unused.".format(n_loops, loop_duration, t_remain))

    for loop in range(1,int(n_loops)):
        t = loop_brown(t)

    print("{:6.1f}: Brownian motion finished.".format(t))
    return t

def phase_agglomerate(time, duration=395-220):
    t0 = time
    t = loop_agglomerate(t0)
    loop_duration= t - t0
    n_loops, t_remain = divmod(duration, loop_duration)
    n_loops = int(n_loops)
    print("        Executing {} agglomeration loops of {:4.1f}s length each. {:4.1f}s unused.".format(n_loops, loop_duration, t_remain))

    for loop in range(1, int(n_loops)):
        t = loop_agglomerate(t)

    print("{:6.1f}: Forced agglomeration finished.".format(t))
    return t




total_time = phase_injection(0)

# Do some initial measurements on the freshly-injected particles
total_time = scan_e(total_time)

# Brownian growth
total_time = phase_brown(total_time)

# Analyse the largest particle grown due to Brownian motion: Phase II
total_time = largest_particle(total_time)

# Use forced agglomeration to grow larger particles: Phase III
# Each takes 36 seconds: 12s electric analysis, 12s squeezing, 12s analysis
total_time = phase_agglomerate(total_time)

# Image the three largest particles grown: Phase IV
for loop in range(0,3):
    total_time = largest_particle(total_time)

# continue until end: Phase V
for loop in range(0,4):
    total_time = loop_agglomerate(total_time)


fig, ax = plt.subplots()
#ax.broken_barh([(110, 30), (150, 10)], (10, 9), facecolors='blue')
#ax.broken_barh([(10, 50), (100, 20), (130, 10)], (20, 9),
               #facecolors=('red', 'yellow', 'green'))
# [(xstart, duration)], (ystart, height), facecolors=('color')
ticks = [0] * len(components)

with open('/home/ingo/idltools/icaps_test.txt', 'w') as thefile:
    for index, item in enumerate(components, start = 1):
        time = components.get(item).on_time
        color = components.get(item).color
        ax.broken_barh(time, (index, 0.5), facecolors=color)
        ticks[index-1] = index
        thefile.write("%s: " % item)
        thefile.write("%s\n" % components.get(item).on_time)
    thefile.close()

ax.set_yticklabels(components)

ax.set_ylim(0, max(ticks)+1)
ax.set_xlim(-100, 600)
ax.set_xlabel('seconds since start of micro-g')

ax.set_yticks(ticks)
ax.grid(True)

# Annotate 2nd injection
ax.annotate('optional 2nd,\ninjection',
                  xy=(17, 26), xycoords='data',
                  xytext=(50, 26), textcoords='data',
                  size=8,
                  arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5))
#ax.annotate('end of µg', xy=(440, 43), xytext=(447, 45.5), textcoords='data', fontsize=8,
#            horizontalalignment='center')


# annotate end of µg
plt.axvline(x=440, ymin=0, ymax = 50, linewidth=1, color='k', linestyle='dashed')

ax.annotate('end of µg', (440, 26), xycoords='data',
            xytext=(470,26), textcoords='data',
            size=8,
            arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5)),


#ax.annotate('Phase I', (50,36), xytext=((22+24*7)/2,37), textcoords='data',
            #fontsize=8, horizontalalignment='center', verticalalignment='top')
#ax.annotate('Phase II', (50,36), xytext=(22+24*7+20,37), textcoords='data',
            #fontsize=8, horizontalalignment='center', verticalalignment='top')
#ax.annotate('Phase III', (50,36), xytext=(42+24*7+36*3+20,37), textcoords='data',
            #fontsize=8, horizontalalignment='center', verticalalignment='top')
#ax.annotate('Phase IV', (50,36), xytext=(42+24*7+36*7+20,37), textcoords='data',
            #fontsize=8, horizontalalignment='center', verticalalignment='top')
#ax.annotate('Brownian motion', (

plt.subplots_adjust(left=0.15)
plt.show()
