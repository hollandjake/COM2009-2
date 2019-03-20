#!/usr/bin/env python3
'''COM2009-3009 EV3DEV TEST PROGRAM'''

# Connect left motor to Output C and right motor to Output B
# Connect an ultrasonic sensor to Input 3

import os
import sys
import time
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


def main():
    '''The main function of our program'''

    # set the console just how we want it
    reset_console()
    set_cursor(OFF)
    set_font('Lat15-Terminus24x12')

    # display something on the screen of the device
    print('Hello World!')

    # print something to the output panel in VS Code
    debug_print('Hello VS Code!')

    # announce program start
    ev3.Sound.speak('Test program starting!').wait()

    # set the motor variables
    mb = ev3.LargeMotor('outB')
    mc = ev3.LargeMotor('outC')
    sp = -25

    # set the ultrasonic sensor variable
    us3 = ev3.UltrasonicSensor('in3')

    # program loop
    for x in range (1, 5):
        
        # fetch the distance
        ds = us3.value()
            
        # display the distance on the screen of the device
        print('Distance =',ds)

        # print the distance to the output panel in VS Code
        debug_print('Distance =',ds)
        
        # announce the distance
        ev3.Sound.speak(ds).wait()

        # move
        mb.run_direct(duty_cycle_sp=sp)
        mc.run_direct(duty_cycle_sp=sp)
        time.sleep(1)

        # stop
        mb.run_direct(duty_cycle_sp=0)
        mc.run_direct(duty_cycle_sp=0)
        
        # reverse direction
        sp = -sp
    
    # announce program end
    ev3.Sound.speak('Test program ending').wait()

if __name__ == '__main__':
    main()
