#!/usr/bin/env python3

import os
import sys
from ev3dev2.sensor import INPUT_3, INPUT_2, INPUT_4, INPUT_1
from ev3dev2.sensor.lego import UltrasonicSensor, GyroSensor
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, MoveTank
from ev3dev2.sound import Sound
from ev3dev2.display import Display
import math
import time
from vector import Vector

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

class DepthSensor:
    RANGE = 2550 # in mm
    def __init__(self,port,angle,offset):
        self.sensor = UltrasonicSensor(port)
        self.angle = angle
        self.offset = offset

    def get_collion_pos(self):
        depth = self.sensor.value()
        depth_vector = Vector.fromAngle(self.angle,depth)
        return self.offset + depth_vector

class Arena:
    def __init__(self, arena_x, arena_y):
        self.display = Display()
        self.display_size = Vector(self.display.xres,self.display.yres)
        debug_print("oof")
        self.occupancy_grid = [[0 for y in range(0,arena_y*2,100)] for x in range(0, arena_x*2,100)]
        debug_print("ding")
        self.size = Vector(arena_x,arena_y)
        self.pixel_size = self.calculate_pixel_size()

    def is_occupied(self,x,y):
        return self.occupancy_grid[round(x/100)][round(y/100)] != 0

    def is_empty(self,x,y):
        return not self.is_occupied(x,y)

    def set_occupancy(self,position,state):
        nearest_x = round(position.x/100)
        nearest_y = round(position.y/100)
        self.occupancy_grid[nearest_x][nearest_y] = state

    def plot(self,robot_pos):
        robot = self.pos_on_display(robot_pos)
        self.display.clear()
        for x in range(0,self.size.x*2):
            for y in range(0, self.size.y*2):
                pos = self.pos_on_display(Vector(x,y))
                self.display.rectangle((pos.x,pos.y,pos.x+pixel_size.x,pos.y+pixel_size.y), fill='red')

        self.display.rectangle((robot_pos.x,robot_pos.y,robot_pos.x+pixel_size.x,robot_pos.y+pixel_size.y), fill='green')
        self.display.update()
        return self.display.image()

    def pos_on_display(self,pos):
        return (self.display_size+pos*self.pixel_size)/2

    def calculate_pixel_size(self):
        display_size = self.display_size #in px
        arena_size = self.size #in mm

        #scale arena_size
        scale_x = display_size.x/arena_size.x
        scale_y = display_size.y/arena_size.y

        scale = min(scale_x,scale_y)
        return Vector(scale,scale)



class Robot:
    DIAMETER_OF_WHEEL_CHASSIS = 0.125 #in m
    ROT_PER_M = 1000/math.pi*DIAMETER_OF_WHEEL_CHASSIS
    DISTANCE_PER_DEGREE = DIAMETER_OF_WHEEL_CHASSIS * math.pi / 360
    ROT_PER_DEG = ROT_PER_M * DISTANCE_PER_DEGREE

    def __init__(self,arena_x,arena_y):
        self.arena = Arena(arena_x,arena_y)

        self.gyro = GyroSensor(INPUT_4)
        self.motors = MoveTank(OUTPUT_B,OUTPUT_C)
        self.speaker = Sound()
        self.left_sensor = DepthSensor(INPUT_2, -90,Vector(-90,90))
        self.right_sensor = DepthSensor(INPUT_3, 90,Vector(90,90))
        self.calibrate()
    
    def calibrate(self):
        self.position = Vector(0,0)
        self.gyro.mode = 'GYRO-CAL'
        self.gyro.mode = 'GYRO-ANG'
        
    def angle(self):
        return self.gyro.value() % 360

    def set_position(self, end_pos):
        movement_vector = end_pos - self.position
        self.set_angle(movement_vector.angle())
        self.move(movement_vector.length())
        self.position = end_pos

    def move(self, distance):
        self.motors.on_for_rotations(100,100,ROT_PER_M*distance)

    def set_angle(self, end_angle):
        end_angle = end_angle % 360
        debug_print(end_angle)
        
        while True:
            start_angle = self.angle()
            debug_print(start_angle, end_angle, abs(end_angle - start_angle))

            if abs(end_angle - start_angle) <= 3 or abs((end_angle + start_angle) % 360) <= 3:
                break
            change = end_angle - start_angle
            if change > 180:
                change = 360 - change
                self.motors.on_for_rotations(-50,50,self.ROT_PER_DEG)
            else:
                self.motors.on_for_rotations(50,-50,self.ROT_PER_DEG)
            

    def scan(self):
        # spin 360Deg and at each degree check for collision data
        pos = self.position
        start_angle = self.angle()
        for a in range(0,360):
            self.set_angle(start_angle+a)
            collision_left = self.left_sensor.get_collion_pos()
            collision_right = self.right_sensor.get_collion_pos()

            self.arena.set_occupancy(pos+collision_left,1)
            self.arena.set_occupancy(pos+collision_right,1)
            
    def calculateTarget(self):
        return self.position+Vector(10,0)

    def plot(self):
        return self.arena.plot()

    def exit(self):
        self.speaker.tone(1000,1,Sound.PLAY_WAIT_FOR_COMPLETE)


def main():
    robot = Robot(3300,3300)

    while True:
        debug_print("Scanning")
        robot.scan()
        debug_print("Targetting")
        target = robot.calculateTarget()
        if target == None:
            robot.exit()
            break
        debug_print("Going to target")
        robot.set_position(target)
        debug_print("Drawing")
        display = robot.plot() #update debug display
        display.show() #Debug


if __name__ == '__main__':
    main()