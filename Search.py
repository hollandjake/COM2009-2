#!/usr/bin/env python3
'''COM2009-3009 EV3DEV TEST PROGRAM'''

# Connect left motor to Output C and right motor to Output B
# Connect an ultrasonic sensor to Input 3

import os
import sys
import time
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_3, INPUT_2
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.led import Leds
import math
import time

# state constants
ON = True
OFF = False


def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)


def reset_console():
    '''Resets the console to the default state'''
    print('\x1Bc', end='')


def set_cursor(state):
    '''Turn the cursor on or off'''
    if state:
        print('\x1B[?25h', end='')
    else:
        print('\x1B[?25l', end='')


def set_font(name):
    '''Sets the console font

    A full list of fonts can be found with `ls /usr/share/consolefonts`
    '''
    os.system('setfont ' + name)


def main():
    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    tank_drive = MoveTank(OUTPUT_B,OUTPUT_C)
    leftSensor = UltrasonicSensor(INPUT_2)
    rightSensor = UltrasonicSensor(INPUT_3)
    leds = Leds()
    leds.set_color("LEFT", "RED")
    leds.set_color("RIGHT", "RED")

    speed = 20 ##TODO we need to find a value between 50 and 100 for which the system still works - 50 would replicate our old functionality and 100 would be twice the speed
    threshold = 300
    factor = 1
    infinity = 2550
    while True:
        dl = leftSensor.value()
        dr = rightSensor.value()

        rl,rr = 1, 1

        if dl < threshold:
            rl += (infinity-dl)*factor

        if dr < threshold:
            rr += (infinity-dr)*factor

        #ratio balancing
        if rl > rr:
            rr = rr/rl
            rl = 1
        else:
            rl = rl/rr
            rr = 1


        debug_print(rl,rr)
        tank_drive.on(rl*-speed,rr*-speed)        

if __name__ == '__main__':
    main()