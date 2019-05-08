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
import random


def levy(mu):
	''' From the Harris Nature paper. '''
	# uniform distribution, in range [-0.5pi, 0.5pi]
	x = random.uniform(-0.5 * math.pi, 0.5 * math.pi)

	# y has a unit exponential distribution.
	y = -math.log(random.uniform(0.0, 1.0))

	a = math.sin( (mu - 1.0) * x ) / (math.pow(math.cos(x), (1.0 / (mu - 1.0))))
	b = math.pow( (math.cos((2.0 - mu) * x) / y), ((2.0 - mu) / (mu - 1.0)) )
    
    #this might break
	return a * b

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

def scan(tank_drive, lightSensor):
    theta = 15
    bestLight = 0
    bestAngle = 0
    for angle in range(0,360,theta):
        rotateDeg(theta)
        sensor = lightSensor.value()
        if bestLight < sensor:
            bestLight = sensor
            angle = bestAngle

    return 

def anyObstacles(leftSensor, rightSensor):
    leftDist = leftSensor.value()
    rightDist = rightSensor.value()

    threshold = 100

    if leftDist > threshold or rightDist > threshold:
        return True
    else
        return False

def levyFlight(tank_drive, theta, leftSensor, rightSensor):
    rotateDeg(theta)
    dist = max(5,min(25,int(levy(1.5)*100)))
    dist = dist/100
    chunks = min(0.1,dist)

    for x in range(0, dist, chunks):
        if anyObstacles(leftSensor,rightSensor):
            return
        moveDist(chunks)





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
        while abs(GYRO - targetAngle) < 4 or abs(GYRO + targetAngle) % 360 < 4:
            if GYRO > targetAngle:
                tank_drive.on_for_rotations(-50,50,0.1)
            else:
                tank_drive.on_for_rotations(50,-50,0.1)
            GYRO = gy.value() % 360

    def moveDist(dist):
        DIAMETER_OF_WHEEL_CHASSIS = 0.125 #in m
        ROT_PER_M = 1000/math.pi*DIAMETER_OF_WHEEL_CHASSIS
        tank_drive.on_for_rotations(100,100,dist*ROT_PER_M)


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
        angle = scan(tank_drive,lightSensor)
        levyFlight(angle)

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