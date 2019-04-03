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
import ev3dev.ev3 as ev3
from ev3dev2.led import Leds
import math
import time

# state constants
ON = True
OFF = False

ROT_M = 5.895 #LargeMotor.count_per_m/LargeMotor.count_per_rot.value


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

    gy = ev3.GyroSensor('in4')
    gy.mode = 'GYRO-CAL'
    gy.mode = 'GYRO-ANG'
    GYRO = gy.value() % 360

    tank_drive = MoveTank(OUTPUT_B,OUTPUT_C)
    leftSensor = UltrasonicSensor(INPUT_2)
    rightSensor = UltrasonicSensor(INPUT_3)

    def moveM(distance):
        tank_drive.on
    
    def rotateDeg(degree,right=True):
        GYRO = gy.value() % 360
        targetAngle = (GYRO + degree) % 360
        while GYRO != targetAngle:
            if GYRO > targetAngle:
                tank_drive.on_for_rotations(-50,50,0.1)
            else:
                tank_drive.on_for_rotations(50,-50,0.1)
            GYRO = gy.value() % 360
    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    speed = 100 ##TODO we need to find a value between 50 and 100 for which the system still works - 50 would replicate our old functionality and 100 would be twice the speed
    threshold = 300
    factor = 1
    infinity = 2550
    while True:
        dl = leftSensor.value()
        dr = rightSensor.value()
        gyro = gy.value() % 360
        debug_print(gyro)

        while time.sleep(0.01):
            tank_drive.on_for_rotations()

        if gyro in range(88,92) or gyro in range(178,182) or gyro in range(268,272) or (gyro in range(358,360) or gyro in range(0,2)):
            tank_drive.on(0,0)
            time.sleep(3)
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

        rotateDeg(90)
        break   



if __name__ == '__main__':
    main()