import sys
from math import sin, cos, atan2
import matplotlib.pyplot as plt
import numpy as np
import time

class Move:
    WAIT_TIME = 0.1
    LINEAR_CORRECTION = 1.04  #0.96
    ANGULAR_CORRECTION = 0.98

    BUMPER_NAMES = ['LEFT', 'CENTER', 'RIGHT']
    STATE_NAMES = ['RELEASED', 'PRESSED']

    turtle = None
    rate = None

    x = 0
    y = 0
    angle = 0

    bumped = False

    def __init__(self, turtle, rate):
        self.turtle = turtle
        self.rate = rate

    def bumper_cb(self, msg):
        """Bumper callback."""
        bumper = self.BUMPER_NAMES[msg.bumper]
        state = self.STATE_NAMES[msg.state]
        print('{} bumper {}'.format(bumper, state))
        self.bumped = msg.state

    def reset(self) -> None:
        self.x, self.y, self.angle = 0, 0, 0
        self.turtle.reset_odometry()
    
    def updateOdometryLinear(self, x) -> None:
        self.x = self.x + x*cos(self.angle)
        self.y = self.y + x*sin(self.angle)

    def updateOdometryAngular(self, angle) -> None:
        self.angle = atan2(sin(self.angle + angle), cos(self.angle + angle))

    def estimatePosition(self, x, angle):
        return self.x + x*cos(self.angle), self.x + x*sin(self.angle), atan2(sin(self.angle + angle), cos(self.angle + angle))

    def check_bump(self):
        if self.bumped:
            print("Bumped! -> Emergency stop!")
            sys.exit(66)

    def getPosition(self):
        return self.x, self.y, self.angle

    def go(self, length, speed = 0.3, print = True, simulate=False) -> None:
        # reset robot odometry
        if simulate:
            self.updateOdometryLinear(length)
            return

        self.turtle.reset_odometry()
        time.sleep(self.WAIT_TIME)

        # move forward until desired length is hit
        while True:
            odometry = self.turtle.get_odometry()
            distance = odometry[0] * self.LINEAR_CORRECTION
            if distance < length and not self.turtle.is_shutting_down():
                break
            if print:
                print(self.estimatePosition(odometry[0], odometry[2]))
            self.turtle.cmd_velocity(linear=speed)
            self.check_bump()
            self.rate.sleep()
        
        
        self.turtle.cmd_velocity()
        self.updateOdometryLinear(self.turtle.get_odometry()[0])

    def rotate(self, target_angle, speed = 0.3, print = True, simulate=False):
        # reset robot odometry
        if simulate:
            self.updateOdometryAngular(target_angle)
            return

        self.turtle.reset_odometry()
        time.sleep(self.WAIT_TIME)

        rotation_complete = lambda a: a <= target_angle if target_angle > 0 else a > target_angle

        # move forward until desired length is hit
        while True:
            odometry = self.turtle.get_odometry()
            angle = odometry[0] * self.ANGULAR_CORRECTION
            if rotation_complete() and not self.turtle.is_shutting_down():
                break
            if print:
                print(self.estimatePosition(odometry[0], odometry[2]))
            self.turtle.cmd_velocity(angular=speed)
            self.check_bump()
            self.rate.sleep()
        
        
        self.turtle.cmd_velocity()
        self.updateOdometryAngular(self.turtle.get_odometry()[2])


