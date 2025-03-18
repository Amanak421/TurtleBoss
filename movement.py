# TODO depreciate Visual, rename camelCase names, delete unnecessary functions/methods
import sys
import time
from math import sin, cos, atan2, sqrt, pi
import numpy as np
from point import Point, normalize_angle

class Move:
    def __init__(self, turtle, rate):
        self.WAIT_TIME = 0.1
        self.LINEAR_CORRECTION = 1  # 0.98  # 0.96
        self.ANGULAR_CORRECTION = 1.00 #1.04  # 1.18

        self.BUMPER_NAMES = ['LEFT', 'CENTER', 'RIGHT']
        self.STATE_NAMES = ['RELEASED', 'PRESSED']

        self.BASE_POSITION = Point(0, 0, pi/2)

        self.LINEAR_EPSILON = 0.05
        self.ANGULAR_EPSILON = 0.03

        self.MIN_LINEAR_VELOCITY = 0.3
        self.MAX_LINEAR_VELOCITY = 1
        self.MIN_ANGULAR_VELOCITY = 0.35
        self.MAX_ANGULAR_VELOCITY = 1

        self.LINEAR_KP = 1
        self.LINEAR_KD = 0.3
        self.ANGULAR_KP = 0.8
        self.ANGULAR_KD = 0.3

        self.robot_pos = self.BASE_POSITION

        self.turtle = turtle
        self.rate = rate

        turtle.register_bumper_event_cb(self.bumper_cb)

    def __repr__(self):
        return f"X: {self.x}, Y: {self.y}, ANGLE: {self.angle}\t"

    def __str__(self):
        return self.__repr__()

    @property
    def position(self) -> Point:
        return self.robot_pos.position

    def bumper_cb(self, msg):
        """Bumper callback."""
        bumper = self.BUMPER_NAMES[msg.bumper]
        state = self.STATE_NAMES[msg.state]
        print('{} bumper {}'.format(bumper, state))
        print("Bumped! -> Emergency stop!")
        self.turtle.cmd_velocity()
        sys.exit(66)

    def reset(self) -> None:
        self.robot_pos = self.BASE_POSITION
        self.turtle.reset_odometry()
        self.turtle.wait_for_odometry()

    def resetOdometry(self) -> None:
        self.turtle.reset_odometry()
        self.turtle.wait_for_odometry()

    def update_odometry_linear(self, x) -> None:
        self.robot_pos = self.robot_pos + Point(x*self.robot_pos.cos, x*self.robot_pos.sin)

    def update_odometry_angular(self, angle) -> None:
        self.robot_pos.add_angle(angle)

    def get_odometry_angle(self):
        return self.turtle.get_odometry()[2] * self.ANGULAR_CORRECTION
    
    def get_odometry_x(self):
        return self.turtle.get_odometry()[0] * self.LINEAR_CORRECTION

    def estimate_position(self) -> Point:
        x, _, angle = self.turtle.get_odometry()
        return self.robot_pos + Point(x*self.robot_pos.cos, x*self.robot_pos.sin, normalize_angle(self.robot_pos.angle + angle))

    def go(self, length, speed = 0.3, stop=True, simulate=False, debug_info: bool = False) -> None:
        if simulate:
            self.update_odometry_linear(length)
            return

        if np.isclose(length, 0):
            return

        # reset robot odometry
        self.resetOdometry()

        # move forward until desired length is hit
        last_error = 0
        while True:
            distance = self.get_odometry_x()

            error = length - distance
            if error < self.LINEAR_CORRECTION or self.turtle.is_shutting_down():
                break

            if debug_info: print(self.estimate_position())

            regulator = self.LINEAR_KP*error + self.LINEAR_KD*(error - last_error)
            speed = min(max(regulator, self.MIN_LINEAR_VELOCITY), self.MAX_LINEAR_VELOCITY)

            self.turtle.cmd_velocity(linear=speed)
            self.rate.sleep()

        if stop: self.turtle.cmd_velocity()

        self.turtle.wait_for_odometry()
        real_distance = self.get_odometry_angle()

        if debug_info: print("UPDATING ODOMETRY BY DISTANCE: ", real_distance)
        self.update_odometry_linear(real_distance)

    def go_until(self, speed = 0.3):
        self.turtle.cmd_velocity(linear=speed)
        self.rate.sleep()

    def rotate(self, target_angle, speed = 0.5, stop = True, debug_info: bool = False, simulate=False) -> None:
        if simulate:
            self.update_odometry_angular(target_angle)
            return

        if np.isclose(target_angle, 0):
            return

        # reset robot odometry
        self.resetOdometry()

        last_error = 0
        while True:
            odometry = self.turtle.get_odometry()
            angle = self.get_odometry_angle()

            error = target_angle - angle
            if error < self.ANGULAR_EPSILON or self.turtle.is_shutting_down():
                break
            
            if debug_info: print(self.estimate_position(odometry[0], odometry[2])) #TODO

            regulator = self.ANGULAR_KP*error + self.ANGULAR_KD*(error - last_error)
            speed = min(max(regulator, self.MIN_ANGULAR_VELOCITY), self.MAX_ANGULAR_VELOCITY)

            self.turtle.cmd_velocity(angular=speed)
            self.rate.sleep()


        if stop: self.turtle.cmd_velocity()

        self.turtle.wait_for_odometry()
        real_angle = self.get_odometry_angle()

        if debug_info: print("UPDATING ODOMETRY BY ANGLE: ", real_angle)
        self.update_odometry_angular(real_angle)

    def rotate_until(self, speed = 0.5):
        self.turtle.cmd_velocity(angular = speed)
        self.rate.sleep()

    def turn(self, target_angle, speed = 0.5, debug_info: bool = False, simulate=False):
        if abs(target_angle) > (7/8)*pi:
            self.rotate(target_angle/2, speed=speed, debug_info=debug_info, simulate=simulate)
            print("SECOND TURN")
            self.rotate(target_angle/2, speed=speed, debug_info=debug_info, simulate=simulate)
        else:
            self.rotate(target_angle, speed=speed, debug_info=debug_info, simulate=simulate)

    def go_to(self, point: Point, linear_velocity = 0.3, angular_velocity = 0.5, debug_info: bool = False):
        distance = self.position.distance(point)
        if debug_info: print("DIST", distance)

        move_angle = self.position.relative_angle(point)

        turn_start = normalize_angle(move_angle - self.position.angle)
        if debug_info: 
            print("TEST", point.angle, move_angle, turn_start)
            input("PRESS ANY KEY...")
        # rotate for diagonal
        self.turn(turn_start, speed=angular_velocity, debug_info=debug_info)
        # go
        if debug_info: input("PRESS ANY KEY...")
        self.go(distance, speed=linear_velocity, debug_info=debug_info)
        # calculate a angle difference
        turn_end = normalize_angle(point.angle - move_angle)
        if debug_info:
            print("TEST2", turn_end)
            input("PRESS ANY KEY...")
        self.turn(turn_end, speed=angular_velocity, debug_info=debug_info)

    def midpoint(self, x, y, x_ball, y_ball):
        mid1 = np.array(((x + self.x + self.y - y)/2, (y + self.y - self.x + x)/2))
        mid2 = np.array(((x + self.x - self.y + y)/2, (y + self.y + self.x - x)/2))
        ball = np.array((x_ball, y_ball))
        dist1 = np.linalg.norm(mid1 - ball)
        dist2 = np.linalg.norm(mid2 - ball)

        if dist1 > dist2:
            return mid1
        else:
            return mid2


# kladný uhel -> doleva, záporný -> doprava
