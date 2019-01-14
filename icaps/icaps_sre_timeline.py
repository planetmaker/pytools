#!/usr/bin/env python3
"""
Make the ICAPS timeline

TODO:
    * LDM light off when OOS light is on
    * OOS illumination must be on during CMS scan +- 1mm
"""
import matplotlib.pyplot as plt
# from matplotlib.patches import Ellipse
from matplotlib.patches import Rectangle
from matplotlib.offsetbox import (TextArea, AnnotationBbox)

components = {}

end_mug = 375 # seconds
brown_time = 150 # seconds
agglomeration_time = 150 # seconds

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
add_component('restore cloud',      'mediumpurple')
add_component('center agglomerate', 'mediumpurple')
add_component('measure cloud v',    'blueviolet')

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
add_component('Forced agglom.',     'lightpink')
add_component('Brownian motion',    'lightpink')

add_component('LDM illumination',   'yellow',      timeslot=(-5,600))
add_component('OOS illumination',   'peru',        timeslot=(-5,600))

add_component('LDM camera',         'olivedrab',   timeslot=(-5,600))
add_component('OOS camera',         'yellowgreen', timeslot=(-5,600))

add_component('analyse injection',  'lightgrey')
add_component('open shutter valve', 'dimgray')
add_component('injection piston',   'gray')
add_component('cogwheel',           'black')

#def OOS_mode(time, duration=0.1):
#    t = add_component_time('OOS illumination', (time, duration))
#    return t
#

def position_particle(time, duration=1):
    t = time
    t = components['center agglomerate'].add_time((time,duration))
    return t
def restore_cloud(time, duration=1):
    t = time
    t = components['restore cloud'].add_time((time,duration))
    return t

def scan(time, direction='z'):
    t = time
    # center particle back and forth, look with LDM, LSU and sometimes also OOS
    t = components['CMS scan -' + direction].add_time((t,3))
    t = components['CMS scan +' + direction].add_time((t,6))
    t = components['CMS scan -' + direction].add_time((t,3))
    return t

def scan_cloud(time):
    t = scan(time)
    components['Scan cloud'].add_time((time,t-time))
    return t

def scan_agglomerate(time):
    t = position_particle(time)
    t_scan = t
    t = scan(t)
    scan(t_scan, direction='x')
    components['Scan agglomerate'].add_time((t_scan, t-t_scan))
    t = restore_cloud(t)
    return t

def loop_brown(time):
    # observe 10s
    t = time

    t_start_levitate = t
    t = components['CMS levitate'].add_time((t, 10))
    # t = adjust_CMS(t)
    t = scan_cloud(t)
    return t

def largest_particle(time):
    t = time
    t = position_particle(t) # 3s
    scan_t = t
    t = scan_agglomerate(t)
    components['Scan agglomerate'].add_time((scan_t, t-scan_t))
    t = restore_cloud(t) # 3
    print("{:6.1f}: Largest particle finished in {:4.1f}s.".format(t,t-time))
    return t

def scan_e(time): # initial scan of the cloud
    t = time
    t = components['CMS E +z'].add_time((t, 0.5))
    t = components['CMS E -z'].add_time((t, 0.5))
    print("        Charge scan particle: {:4.1f}".format(t-time))
    return t

def loop_agglomerate(time):
    t = time
    # squeezing
    t = components['CMS squeeze'].add_time((t, 15))
    # scan
    t = scan_cloud(t)
    components['Forced agglom.'].add_time((time,t-time))
    print("        Loop agglomerate: {:4.1f}".format(t-time))
    return t

#################################################
#### Define the actual sequences below here #####
#################################################
#
#
def phase_injection(time):
    t = time
    # First 22 seconds are injection. That's directly defined above in the item definitions
    components['cogwheel'].add_time((-30,60))

    relaxation_time = 7.5

    # First injection
    t = components['injection piston'].add_time((-1,6))
    components['open shutter valve'].add_time((0,5))
    t_end_injection1 = t
    t = components['analyse injection'].add_time((t_end_injection1,relaxation_time))
    components['measure cloud v'].add_time((t_end_injection1,relaxation_time-2))
    scan_e(t_end_injection1+relaxation_time-1)
    #total_time = scan_e(total_time)

#    # possible re-injection
    components['injection piston'].add_time((t,6))
    t = components['open shutter valve'].add_time((t+1,5))
    t_end_injection2 = t
    t = components['analyse injection'].add_time((t_end_injection2,relaxation_time))
    components['measure cloud v'].add_time((t_end_injection2,relaxation_time-2))
    scan_e(t_end_injection2+relaxation_time-1)

    print("{:6.1f}: Injection finished".format(t))
    return t
#
def phase_brown(time, duration=brown_time):
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

    components['Brownian motion'].add_time((t0, t-t0))

    print("{:6.1f}: Brownian motion finished.".format(t))
    return t

def phase_agglomerate(time, duration=agglomeration_time):
    # electric measurement
    t = time
    t = components['CMS E +z'].add_time((t,2))
    t = components['CMS E -z'].add_time((t,4))
    t = components['CMS E +z'].add_time((t,2))
    t0 = t
    t = loop_agglomerate(t0)
    loop_duration= t - t0
    n_loops, t_remain = divmod(duration-2*8, loop_duration) # reduce by E-scan at start and end
    n_loops = int(n_loops)
    print("        Executing {} agglomeration loops of {:4.1f}s length each. {:4.1f}s unused.".format(n_loops, loop_duration, t_remain))

    for loop in range(1, int(n_loops)):
        t = loop_agglomerate(t)

    # Final E-scan
    t = components['CMS E +z'].add_time((t,2))
    t = components['CMS E -z'].add_time((t,4))
    t = components['CMS E +z'].add_time((t,2))

    print("{:6.1f}: Forced agglomeration finished.".format(t))
    return t
#
#
#
#
total_time = phase_injection(0)
injection_time = total_time

# Do some initial measurements on the freshly-injected particles (part of injection)
#total_time = scan_e(total_time)
scan_e_time = total_time

# Brownian growth
start_brown = total_time
total_time = phase_brown(total_time, duration=180)

# Analyse the largest particle grown due to Brownian motion: Phase II
total_time = largest_particle(total_time)

# Use forced agglomeration to grow larger particles: Phase III
# Each takes 36 seconds: 12s electric analysis, 12s squeezing, 12s analysis
start_agglomerate = total_time
total_time = phase_agglomerate(total_time, duration=120)

# Image the three largest particles grown: Phase IV

end_agglomerate = total_time
for loop in range(0,3):
    total_time = largest_particle(total_time)

# continue until end: Phase V
for loop in range(0,4):
    total_time = loop_agglomerate(total_time)
#
#
fig, ax = plt.subplots()
plt.setp(ax, zorder=0)
##ax.broken_barh([(110, 30), (150, 10)], (10, 9), facecolors='blue')
##ax.broken_barh([(10, 50), (100, 20), (130, 10)], (20, 9),
#               #facecolors=('red', 'yellow', 'green'))
## [(xstart, duration)], (ystart, height), facecolors=('color')
ticks = [0] * len(components)
#
with open('/home/ingo/idltools/icaps_test.txt', 'w') as thefile:
    for index, item in enumerate(components, start = 1):
        dutycycle = components.get(item).dutycycle
        color = components.get(item).color
        ax.broken_barh(dutycycle, (index, 0.5), facecolors=color)
        ticks[index-1] = index
        thefile.write("%s: " % item)
        thefile.write("%s\n" % dutycycle)
    thefile.close()
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
ax.annotate('optional 2nd,\ninjection',
                  xy=(17, ymax-2), xycoords='data',
                  xytext=(50, ymax-2), textcoords='data',
                  size=8,
                  arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5))

ax.annotate('end of µg', (end_mug, ymax-2), xycoords='data',
            xytext=(end_mug+20,ymax-2), textcoords='data',
            size=8,
            arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5)),

#ax.annotate('end of µg', xy=(end_mug+20, ymax-2), xytext=(end_mug+20, ymax-2), textcoords='data', fontsize=8,
#            horizontalalignment='center')


# Annotate scan for charges
ycharge = 10
rect = Rectangle((7.5,ycharge),scan_e_time+2,2,fill=False,color='black',linewidth=1.5,linestyle='-')
#rect = Rectangle((0.5,0.5),0.1,0.1,fill=True,color='black',linewidth=5,linestyle='-',figure=ax)
ax.add_patch(rect)
ax.annotate('short scan for charge\n0.5s each direction\nafter injection(s)', (scan_e_time+10, ycharge), xycoords='data',
            xytext=(scan_e_time+25, ycharge), textcoords='data',
            size=8,
            arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5))

# annotate different phases
ax.annotate('Brownian phase', (start_brown+(start_agglomerate - start_brown) / 2, ymax), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('Agglomeration phase', (start_agglomerate+(end_agglomerate - start_agglomerate) / 2, ymax), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('Scan', (end_agglomerate+(end_mug - end_agglomerate) / 2, ymax), textcoords='data',
            size=10, horizontalalignment='center')

# indicate exact times
uppery = 0.95
plt.axvline(x=start_brown, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
plt.axvline(x=start_agglomerate, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
plt.axvline(x=end_agglomerate, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
# annotate end of µg
plt.axvline(x=end_mug, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')

ax.annotate('{:3.0f}s'.format(start_brown), (start_brown+5, ymax), textcoords='data',
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
text_scandir = TextArea("Adjust such that agglomerates are scanned\nin the viewing direction of the LDM", minimumdescent=False)
ab = AnnotationBbox(text_scandir, (tmin+30, 2.7),
                    xybox=(5, 6.5), # center of text box in data coordinates
                    xycoords='data',
                    boxcoords="data"
                    )
ax.add_artist(ab)


text_scandir = TextArea("Note:\nSequence assumes that\n the LDM camera cannot\n see the OOS light and\n vice versa (e.g. that\n colour filters are used)", minimumdescent=False)
ab2 = AnnotationBbox(text_scandir, (422, 1),
                    xybox=(417, 1.7), # center of text box in data coordinates
                    xycoords='data',
                    boxcoords="data"
                    )
ax.add_artist(ab2)


plt.subplots_adjust(left=0.15)
plt.show()
