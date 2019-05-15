#!/usr/bin/env python3
'''COM2009-3009 EV3DEV TEST PROGRAM'''

#PLAN

# Begin by panning around 360 if light above Threshold then head towards it 
# using the ultrasonic to detect walls
# Using old code from previous do obstacle avoidance
# Gotta stop at light

# Connect left motor to Output C and right motor to Output B
# Connect an ultrasonic sensor to Input 3

import os
import sys
import time
import math
import ev3dev.ev3 as ev3

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

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

class PIDController:
    def __init__(self, Ku=6, Tu=0.3):
        self.Kp = 0.6 * Ku
        self.Ki = (1.2 * Ku) / Tu
        self.Kd = (3 * Ku * Tu) / 40
        
        self.sp = 50
        self.reset()

    def reset(self):
        self.integral = 0
        self.derivative = 0
        self.lastError = 0

    def calculate_motors(self, l_sen, r_sen, d_time):
        error = (l_sen-r_sen)/2
        self.integral += (error * d_time)/100
        self.derivative = error - self.lastError

        self.lastError = error

        val = self.Kp * error + self.Ki * self.integral + self.Kd * self.derivative / d_time
        debug_print(val)
        val = clamp(val, -1000, 1000)

        # calculate final motor speeds using PID value, clamp it between 0-100
        l_sp = clamp(self.sp-val/15, 0, 100)
        r_sp = clamp(self.sp+val/15, 0, 100)

        return l_sp, r_sp
            
def main():
    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    # set the motor variables
    mb = ev3.LargeMotor('outB') # left
    mc = ev3.LargeMotor('outC') # right

    # set the ultrasonic sensor variable
    us2 = ev3.UltrasonicSensor('in2') # left
    us3 = ev3.UltrasonicSensor('in3') # right
    ls1 = ev3.ColorSensor('in1')
    ls1.mode = 'COL-AMBIENT'

    controller = PIDController()

    reset_period = 2

    c_time = time.time()
    end_time = time.time() + reset_period
    while True:
        l_time = c_time
        c_time = time.time()
        # reset the pid controller every reset period
        if c_time > end_time:
            controller.reset()
            end_time = c_time + reset_period
        d_time = c_time-l_time


        l_sp, r_sp = controller.calculate_motors(us2.value(), us3.value(), d_time)

        light = ls1.value()
        if (light > 25):
            print("LIGHT AT"+str(c_time)+" Intesity:"+str(light))
            exit()

        debug_print("l_sp: ", l_sp, ", r_sp: ", r_sp, light)
        mb.run_direct(duty_cycle_sp=l_sp)
        mc.run_direct(duty_cycle_sp=r_sp)

        time.sleep(0.05)

if __name__ == '__main__':
    main()
