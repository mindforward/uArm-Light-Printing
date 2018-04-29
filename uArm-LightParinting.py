#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Fred Chung <fred@mindforward.com>
# Draw for YZ Plane [Light Painting Mode]

import sys, csv, os, math
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from uf.wrapper.swift_api import SwiftAPI
from uf.utils.log import *

logger_init(logging.INFO)

RTIMER = 60
SPECTRUM_MODE = True;
if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
else:
    DATA_FILE = "Rectangle.csv"


def get_spectrum(radians):
    nR = math.cos(radians) * 127 + 128
    nG = math.cos(radians + 2 * math.pi / 3) * 127 + 128
    nB = math.cos(radians + 4 * math.pi / 3) * 127 + 128
    return [nR, nG, nB]
    
def spectrum_to_string(color):
    return "R" + str(int(color[0]))+ " G" + str(int(color[1])) + " B" + str(int(color[2]))

def hex_to_rgb(value):
    #value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))   

print('setup swift ...')

swift = SwiftAPI() # default by filters: {'hwid': 'USB VID:PID=2341:0042'}

print('sleep 2 sec ...')
sleep(2)

print('device info: ')
print(swift.get_device_info())

swift.set_position(190, 0, 50, speed = 5000, timeout = 20)
swift.flush_cmd() # avoid follow 5 command timeout

sleep(3)

# init the RGB led for pin 4
swift.send_cmd_async("M2305 P4 N1 V1")
randian = 1

# Get CSV path file
print(os.path.dirname(os.path.abspath(__file__)))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open(os.getcwd()+'/'+DATA_FILE,newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',') 
        for row in reader:
            if row[0] != "C": # ignore command 
                if row[3] == "R": # spectrum mode
                    # increment the color index
                    randian = randian + 1
                    color = get_spectrum(randian/RTIMER)
                else:
                    color = hex_to_rgb(row[3])
    
                rgb = spectrum_to_string(color)  
                swift.set_position(y = row[1], z = row[2])
                #swift.flush_cmd()
                print(row)
                
                if row[0] == "D":
                    swift.flush_cmd()
                    sleep(0.5)
                    swift.send_cmd_async("M2307 P4 V0 "+rgb)
                elif row[0] == "U":
                    swift.flush_cmd()
                    sleep(0.5)
                    swift.send_cmd_async("M2307 P4 V0 R0 G0 B0")
                elif row[0] == "M":
                    swift.send_cmd_async("M2307 P4 V0 "+rgb)

swift.set_buzzer()

print('done ...')
while True:
    sleep(1)