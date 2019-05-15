#!/usr/bin/env python3
'''COM2009-3009 EV3DEV TEST PROGRAM'''

# Connect left motor to Output C and right motor to Output B
# Connect an ultrasonic sensor to Input 3

import os
import sys
import time
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_3, INPUT_2, INPUT_1, INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor, GyroSensor
import ev3dev.ev3 as ev3
from ev3dev2.led import Leds
import math
import time
import random

class RunningStats:
    # The following are to calculate the running stats

    def __init__(self):
        self.m_n = 0
        self.m_oldM = 0
        self.m_newM = 0
        self.m_oldS = 0
        self.m_newS = 0

    # @staticmethod
    def push(self, x):
        self.m_n = self.m_n + 1

        if (self.m_n == 1):
            # Double check it
            # TODO
            self.m_newM = x
            self.m_oldM = x
            self.m_oldS = 0.0
        else:
            self.m_newM = self.m_oldM + (x - self.m_oldM)/self.m_n
            self.m_newS = self.m_oldS + (x - self.m_oldM)*(x - self.m_newM)
            # set up for next iteration
            self.m_oldM = self.m_newM
            self.m_oldS = self.m_newS

    # Calculates the running variance
    def variance(self):
        # Changed to greater or equals to make sure that the value will
        # be different than 0
        # When the variable is greater, returns the equation
        if (self.m_n > 1):
            return (self.m_newS)/(self.m_n-1)
        else:
            return 0.0

    # Calculates the running standard deviation

    def standard_deviation(self):
        return math.sqrt(self.variance())

    # Calculates the running mean
    def mean(self):
        # Changed to greater or equals to make sure that the value will be
        # different than 0
        if (self.m_n >= 1):
            return self.m_newM
        else:
            return 0.0


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

def main():
    gyro = GyroSensor(INPUT_4)
    gyro.mode = GyroSensor.MODE_GYRO_CAL
    gyro.mode = GyroSensor.MODE_GYRO_ANG

    tank_drive = MoveTank(OUTPUT_B,OUTPUT_C)
    leftSensor = UltrasonicSensor(INPUT_2)
    rightSensor = UltrasonicSensor(INPUT_3)
    lightSensor = ColorSensor(INPUT_1)
    lightSensor.mode = ColorSensor.MODE_COL_AMBIENT
    rmean = RunningStats()

    def scan():
        debug_print("SCAN")

        theta = 5 #deg
        bestAngle = 0
        bestLight = 0
        
        tank_drive.on(25,-25)
        for angle in range(0,360,theta):
            debug_print(angle)
            gyro.wait_until_angle_changed_by(theta)
            sensor = lightSensor.value()
            rmean.push(sensor)
            if (rmean.standard_deviation() + rmean.mean()) < sensor:
                while (rmean.standard_deviation()*3 + rmean.mean()) < sensor and sensor > 20:
                    sensor = lightSensor.value()
                    debug_print("DO YOU HAVE LAMP")
                    tank_drive.stop()
                return
            
            if sensor > bestLight:
                bestLight = sensor
                bestAngle = angle

        debug_print(bestAngle, bestLight)
        gyro.wait_until_angle_changed_by(bestAngle)

    def anyObstacles():
        leftDist = leftSensor.value()
        rightDist = rightSensor.value()
        light = lightSensor.value()

        debug_print(leftDist, rightDist)

        threshold = 100 #mm

        rmean.push(light)
        while (rmean.standard_deviation()*3 + rmean.mean()) < light and light > 20:
            light = lightSensor.value()
            debug_print("DO YOU HAVE LAMP")
            tank_drive.stop()

        if ((leftDist < threshold) or (rightDist < threshold)):
            return True
        else:
            return False

    def levyFlight(x = 0):
        debug_print("LEVY")
        if x == 0:
            x = 11-max(1,min(10,int(levy(1.5)*100)))
            debug_print(x)
        start = time.time()

        debug_print("DRIVE")
        while time.time() - start < x:
            tank_drive.on(50,50)
            if anyObstacles():
                tank_drive.on_for_rotations(-50,-50,1)
                debug_print("OBSTACLE")
                break
        tank_drive.stop()

    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    levyFlight(10)

    while True:
        scan()
        levyFlight()

if __name__ == '__main__':
    main()