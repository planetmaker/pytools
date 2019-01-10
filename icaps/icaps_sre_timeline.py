#!/usr/bin/env python3
"""
Make the ICAPS timeline
"""
import matplotlib.pyplot as plt
# from matplotlib.patches import Ellipse
from matplotlib.patches import Rectangle

components = {}
fps_streaming = 250
fps_burst     = 1000

end_mug = 440 # seconds

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
add_component('center particle',    'mediumpurple')
add_component('adjust CMS',         'darkorchid')
add_component('measure cloud v',    'blueviolet')
add_component('CMS levitate',       'slateblue')
add_component('CMS squeeze',        'slateblue')

add_component('OOS illumination',   'peru')
add_component('LDM illumination',   'yellow')

add_component('CMS scan -x 1mm/s',  'skyblue')
add_component('CMS scan +x 1mm/s',  'deepskyblue')
add_component('CMS E -x',           'steelblue')
add_component('CMS E +x',           'dodgerblue')
add_component('CMS E -y',           'steelblue')
add_component('CMS E +y',           'dodgerblue')
add_component('CMS E -z',           'steelblue')
add_component('CMS E +z',           'dodgerblue')

add_component('scan particle',      'palevioletred')
add_component('Forced agglom.',     'lightpink')
add_component('Brownian motion',    'lightpink')

add_component('LDM read-out',       'olive', ctype=Camera)
add_component('LDM high-speed',     'olive', ctype=Camera)
add_component('LDM stream',         'darkolivegreen', ctype=Camera)
add_component('LDM stream power',   'olivedrab',   timeslot=(-5,600))
add_component('OOS camera',         'yellowgreen', timeslot=(-5,600))

add_component('analyse injection',  'lightgrey')
add_component('open shutter valve', 'dimgray')
add_component('injection piston',   'gray')
add_component('cogwheel',           'black')

#def OOS_mode(time, duration=0.1):
#    t = add_component_time('OOS illumination', (time, duration))
#    return t
#
def LDM_readout(time, duration=0.2):
    t = time
    components['LDM read-out'].add_time((time, duration))
    t= components['OOS illumination'].add_time((time, duration))
    return t

def LDM_highspeed(time, duration=0.02):
    t = time
    components['LDM high-speed'].add_time((t, duration))
    t = components['LDM illumination'].add_time((t, duration))
#    components['OOS illumination'].add_time((t, duration))
#    t = components['LDM read-out'].add_time((t, duration))
    return t

def LDM_stream(time, duration=0.1):
    t = time
    components['LDM stream'].add_time((t, duration))
    t = components['LDM illumination'].add_time((t, duration))
    return t
#
def OOSLDM_mixed_mode(time, duration=0.1):
#    t = time
#    n = round(duration / 0.04)
#    unused_time = (duration+0.0005) % 0.04
#    if unused_time > 0.001:
#        print("No multiple of 40ms defined as mixed mode sequence! Unused time: " + str(unused_time))
#    # Alternatingly use OOS and LDM
#    for count in range(0, int(n)):
#        startt = t
#        t = components['LDM illumination'].add_time((t,0.02))
#        components['LDM stream',    (startt, 0.02))
#        t = components['OOS illumination'].add_time((t,0.02))
#    return t
    components['LDM illumination'].add_time((time, duration))
    components['LDM stream'].add_time((time, duration), fps=fps_streaming)
    t = components['OOS illumination'].add_time((time, duration))
#    components['LDM illumination'].add_time((time, duration))
#    components['LDM stream'].add_time((time, duration))
#    t = components['OOS illumination'].add_time((time, duration))
    return t
#
def adjust_CMS(time):
    t = time
    t = components['measure cloud v'].add_time((t,1))
    t = components['adjust CMS'].add_time((t,1))
    OOSLDM_mixed_mode(time,t-time)
    return t
def position_particle(time):
    t = time
    t = OOSLDM_mixed_mode(t,3)
    components['center particle'].add_time((time,t-time))
    return t
def restore_cloud(time):
    t = time
    t = OOSLDM_mixed_mode(t,3)
    components['restore cloud'].add_time((time,t-time))
    return t

def scan_cloud(time):
    t = time
    # center particle back and forth, look with LDM, LSU and sometimes also OOS
    t = components['CMS scan +x 1mm/s'].add_time((t,3))
    t = components['CMS scan -x 1mm/s'].add_time((t,6))
    t = components['CMS scan +x 1mm/s'].add_time((t,3))
#    LDM_highspeed(time,t-time)
#    t = LDM_readout(t, t-time)
    LDM_stream(time, t-time)
    return t
def scan(time):
    t = time
    t = scan_cloud(t)
    return t

def loop_brown(time, add_readout=0):
    # observe 10s
    t = time
    t = LDM_highspeed(time,1) # observe unperturbed 1s
    t = LDM_readout(t, 4)

    if add_readout != 0:
        t = LDM_readout(t, add_readout)

    t_start_levitate = t
    t = OOSLDM_mixed_mode(t,6) # observe unperturbed, but levitate
    components['CMS levitate'].add_time((time,t-t_start_levitate))
    # t = adjust_CMS(t)
    t = scan_cloud(t)
    return t

def largest_particle(time):
    t = time
    t = adjust_CMS(t)    # 2s
    t = position_particle(t) # 3s
    scan_t = t
    t = scan(t) # 12s
    components['scan particle'].add_time((scan_t,t-scan_t))
    t = restore_cloud(t) # 3
    print("{:6.1f}: Largest particle finished in {:4.1f}s.".format(t,t-time))
    return t

def scan_e(time): # initial scan of the cloud
    t = time
    t = components['CMS E +x'].add_time((t, 0.5))
    t = components['CMS E -x'].add_time((t, 0.5))
    t = components['CMS E +y'].add_time((t, 0.5))
    t = components['CMS E -y'].add_time((t, 0.5))
    t = components['CMS E +z'].add_time((t, 0.5))
    t = components['CMS E -z'].add_time((t, 0.5))
    LDM_highspeed(time, t-time)
    print("        Charge scan particle: {:4.1f}".format(t-time))
    return t

def loop_agglomerate(time):
    t = time
    # electric measurement
    t = components['CMS E +x'].add_time((t,2))
    t = components['CMS E -x'].add_time((t,4))
    t = components['CMS E +x'].add_time((t,2))
    OOSLDM_mixed_mode(time,t-time)
    # squeezing
    components['CMS squeeze'].add_time((t, 15))
    t = OOSLDM_mixed_mode(t,15)
    # scan
    t = scan(t)
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
    components['injection piston'].add_time((-1,6))
    components['open shutter valve'].add_time((0,5))

    t = components['analyse injection'].add_time((5,20))
    OOSLDM_mixed_mode(-1,t+1)
#
#    # possible re-injection
    components['open shutter valve'].add_time((15,5))
    components['injection piston'].add_time((14,6))
    print("{:6.1f}: Injection finished".format(t))
    return t
#
def phase_brown(time, duration=202-22):
    # brownian motion first, Phase I
    # Each takes 24 seconds: 2s CMS adjustment, 10s nothing, 12s analysis
    t0 = time
    t = loop_brown(t0, add_readout=3)
    loop_duration = t - t0
    n_loops, t_remain = divmod(duration, loop_duration)
    n_loops = int(n_loops)
    print("        Executing {} Brown loops of {:4.1f}s length each. {:4.1f}s unused.".format(n_loops, loop_duration, t_remain))

    for loop in range(1,int(n_loops)):
        t = loop_brown(t)

    components['Brownian motion'].add_time((t0, t-t0))

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
#
#
#
#
total_time = phase_injection(0)
injection_time = total_time

# Do some initial measurements on the freshly-injected particles
total_time = scan_e(total_time)
scan_e_time = total_time

# Brownian growth
start_brown = total_time
total_time = phase_brown(total_time)

# Analyse the largest particle grown due to Brownian motion: Phase II
total_time = largest_particle(total_time)

# Use forced agglomeration to grow larger particles: Phase III
# Each takes 36 seconds: 12s electric analysis, 12s squeezing, 12s analysis
start_agglomerate = total_time
total_time = phase_agglomerate(total_time)

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
ax.set_xlim(-100, 600)
ax.set_xlabel('seconds since start of micro-g')
#
ax.set_yticks(ticks)
ax.grid(True)

# Annotate 2nd injection
ax.annotate('optional 2nd,\ninjection',
                  xy=(17, 26), xycoords='data',
                  xytext=(50, 26), textcoords='data',
                  size=8,
                  arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5))
ax.annotate('end of µg', xy=(440, 43), xytext=(447, 45.5), textcoords='data', fontsize=8,
            horizontalalignment='center')


# Annotate scan for charges
rect = Rectangle((scan_e_time-10,11),20,6,fill=False,color='black',linewidth=1.5,linestyle='-')
#rect = Rectangle((0.5,0.5),0.1,0.1,fill=True,color='black',linewidth=5,linestyle='-',figure=ax)
ax.add_patch(rect)
ax.annotate('short scan for charge\n0.5s each direction', (scan_e_time+10, 12), xycoords='data',
            xytext=(scan_e_time+25, 11.5), textcoords='data',
            size=8,
            arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5))

# annotate different phases
ax.annotate('Brownian phase', (start_brown+(start_agglomerate - start_brown) / 2, 28), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('Agglomeration phase', (start_agglomerate+(end_agglomerate - start_agglomerate) / 2, 28), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('Scan', (end_agglomerate+(end_mug - end_agglomerate) / 2, 28), textcoords='data',
            size=10, horizontalalignment='center')

# indicate exact times
uppery = 0.95
plt.axvline(x=start_brown, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
plt.axvline(x=start_agglomerate, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
plt.axvline(x=end_agglomerate, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')
# annotate end of µg
plt.axvline(x=end_mug, ymin=0, ymax = uppery, linewidth=1, color='k', linestyle='dashed')

ax.annotate('{:3.0f}s'.format(start_brown), (start_brown+5, 28), textcoords='data',
            size=10, horizontalalignment='left')
ax.annotate('{:3.0f}s'.format(start_agglomerate), (start_agglomerate, 28), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('{:3.0f}s'.format(end_agglomerate), (end_agglomerate, 28), textcoords='data',
            size=10, horizontalalignment='center')
ax.annotate('{:3.0f}s'.format(end_mug), (end_mug, 28), textcoords='data',
            size=10, horizontalalignment='center')

ax.annotate('end of µg', (end_mug, 26), xycoords='data',
            xytext=(470,26), textcoords='data',
            size=8,
            arrowprops=dict(facecolor='black', shrink=-5, width=1, headwidth=5, headlength=5)),



#
#
##ax.annotate('Phase I', (50,36), xytext=((22+24*7)/2,37), textcoords='data',
#            #fontsize=8, horizontalalignment='center', verticalalignment='top')
##ax.annotate('Phase II', (50,36), xytext=(22+24*7+20,37), textcoords='data',
#            #fontsize=8, horizontalalignment='center', verticalalignment='top')
##ax.annotate('Phase III', (50,36), xytext=(42+24*7+36*3+20,37), textcoords='data',
#            #fontsize=8, horizontalalignment='center', verticalalignment='top')
##ax.annotate('Phase IV', (50,36), xytext=(42+24*7+36*7+20,37), textcoords='data',
#            #fontsize=8, horizontalalignment='center', verticalalignment='top')
##ax.annotate('Brownian motion', (
#
plt.subplots_adjust(left=0.15)
plt.show()
