import sys
import numpy as np
from geometry import Point, normalize_angle
import find_ball
from mapping import Map, has_all


class Robot:
    def __init__(self, turtle, rate):
        self.WAIT_TIME = 0.1
        self.LINEAR_CORRECTION = 0.98 #1  # 0.98  # 0.96
        self.ANGULAR_CORRECTION = 1 #1.04  # 1.18

        self.BUMPER_NAMES = ['LEFT', 'CENTER', 'RIGHT']
        self.STATE_NAMES = ['RELEASED', 'PRESSED']

        self.BASE_POSITION = Point(0, 0, np.pi/2)

        self.LINEAR_EPSILON = 0.01
        self.ANGULAR_EPSILON = 0.03

        self.MIN_LINEAR_VELOCITY = 0.1
        self.MAX_LINEAR_VELOCITY = 0.3
        self.MIN_ANGULAR_VELOCITY = 0.35
        self.MAX_ANGULAR_VELOCITY = 1

        self.LINEAR_KP = 1.5
        self.LINEAR_KD = 0.5
        self.ANGULAR_KP = 1 #0.8
        self.ANGULAR_KD = 0.5 #0.3

        self.robot_pos = self.BASE_POSITION

        self.bumped = False
        self.button = False

        self.turtle = turtle
        self.rate = rate

        turtle.register_bumper_event_cb(self.bumper_cb)
        turtle.register_button_event_cb(self.button_cb)

    def __repr__(self):
        return f"X: {self.robot_pos.x}, Y: {self.robot_pos.y}, ANGLE: {self.angle}\t"

    def __str__(self):
        return self.__repr__()

    @property
    def position(self):
        return self.robot_pos

    @property
    def xya(self):
        return self.robot_pos.xya
    
    @property
    def xy(self):
        return self.robot_pos.xy

    @property
    def angle(self):
        return self.robot_pos.angle

    def bumper_cb(self, msg):
        """Bumper callback."""
        bumper = self.BUMPER_NAMES[msg.bumper]
        state = self.STATE_NAMES[msg.state]
        print('{} bumper {}'.format(bumper, state))
        print("Bumped! -> Emergency stop!")
        self.bumped = True

    def button_cb(self, msg):
        """Button callback."""
        button = self.BUMPER_NAMES[msg.button]
        state = self.STATE_NAMES[msg.state]
        print('{} button {}'.format(button, state))
        self.button = True

    def check_bumper(self):
        if self.bumped:
            self.turtle.cmd_velocity()
            sys.exit(66)

    def reset(self) -> None:
        self.robot_pos = self.BASE_POSITION
        self.turtle.reset_odometry()
        self.turtle.wait_for_odometry()

    def reset_odometry(self) -> None:
        self.turtle.reset_odometry()
        self.turtle.wait_for_odometry()

    def stop(self):
        self.turtle.cmd_velocity()

    def update_odometry_linear(self, x) -> None:
        self.robot_pos = self.robot_pos + Point(x*self.robot_pos.cos, x*self.robot_pos.sin)

    def update_odometry_angular(self, angle) -> None:
        self.robot_pos.add_angle(angle)

    def get_odometry_angle(self, use_correction = True):
        if use_correction:
            return self.turtle.get_odometry()[2] * self.ANGULAR_CORRECTION
        else:
            return self.turtle.get_odometry()[2]
    
    def get_odometry_x(self, use_correction = True):
        if use_correction:
            return self.turtle.get_odometry()[0] * self.LINEAR_CORRECTION
        else:
            return self.turtle.get_odometry()[0]

    def estimate_position(self) -> Point:
        x, _, angle = self.turtle.get_odometry()
        return self.robot_pos + Point(x*self.robot_pos.cos, x*self.robot_pos.sin, normalize_angle(self.robot_pos.angle + angle))

    def go(self, length, set_speed = None, stop=True, simulate=False, use_correction = True, debug_info: bool = False) -> None:
        if simulate:
            self.update_odometry_linear(length)
            return

        if np.isclose(length, 0):
            print("LINEAR REJECTED")
            return

        # reset robot odometry
        self.reset_odometry()

        # move forward until desired length is hit
        last_error = 0
        while True:
            distance = self.get_odometry_x(use_correction = use_correction)

            error = length - distance
            if abs(error) < self.LINEAR_EPSILON or self.turtle.is_shutting_down():
                break

            if debug_info: print(f"{self.estimate_position()}")

            regulator = self.LINEAR_KP*error + self.LINEAR_KD*(error - last_error)
            speed = min(max(regulator, self.MIN_LINEAR_VELOCITY), self.MAX_LINEAR_VELOCITY)
            if set_speed is not None:
                speed = set_speed

            self.turtle.cmd_velocity(linear=speed)
            self.check_bumper()
            self.rate.sleep()

        if stop: self.turtle.cmd_velocity()

        self.turtle.wait_for_odometry()
        real_distance = self.get_odometry_x(use_correction = use_correction)

        if debug_info: print("UPDATING ODOMETRY BY DISTANCE: ", real_distance)
        self.update_odometry_linear(real_distance)

    def go_until(self, speed = 0.3):
        self.turtle.cmd_velocity(linear=speed)
        self.check_bumper()
        self.rate.sleep()

    def kick(self, target_distance, speed=0.8):
        self.reset_odometry()

        # move forward until desired length is hit
        while True:
            distance = self.get_odometry_x()
            if distance > target_distance or self.turtle.is_shutting_down():
                break

            self.turtle.cmd_velocity(linear=speed)
            self.rate.sleep()

        self.turtle.cmd_velocity()

    def rotate(self, target_angle, speed = 0.5, stop = True, use_correction = True, debug_info: bool = False, simulate=False) -> None:
        if simulate:
            self.update_odometry_angular(target_angle)
            return

        if np.isclose(target_angle, 0):
            print("ROTATE REJECTED")
            return

        # reset robot odometry
        self.reset_odometry()

        dir_coef = 1 if target_angle >= 0 else -1
        last_error = 0
        while True:
            angle = self.get_odometry_angle(use_correction = use_correction)

            error = abs(target_angle) - abs(angle)
            if debug_info: print("ROT ERROR", error)
            if abs(error) < self.ANGULAR_EPSILON or self.turtle.is_shutting_down():
                break
            
            if debug_info: print(self.estimate_position())

            regulator = self.ANGULAR_KP*error + self.ANGULAR_KD*(error - last_error)
            speed = min(max(regulator, self.MIN_ANGULAR_VELOCITY), self.MAX_ANGULAR_VELOCITY)

            self.turtle.cmd_velocity(angular=dir_coef*speed)
            self.check_bumper()
            self.rate.sleep()


        if stop: self.turtle.cmd_velocity()

        self.turtle.wait_for_odometry()
        real_angle = self.get_odometry_angle(use_correction = use_correction)

        if debug_info: print("UPDATING ODOMETRY BY ANGLE: ", real_angle, "FINAL ERROR:", target_angle - real_angle)
        self.update_odometry_angular(real_angle)

    def rotate_until(self, speed = 0.5):
        self.turtle.cmd_velocity(angular = speed)
        self.check_bumper()
        self.rate.sleep()

    def turn(self, target_angle, speed = 0.5, debug_info: bool = True, simulate=False):
        if abs(target_angle) > (7/8)*np.pi:
            self.rotate(target_angle/2, speed=speed, debug_info=debug_info, simulate=simulate)
            print("SECOND TURN")
            self.rotate(target_angle/2, speed=speed, debug_info=debug_info, simulate=simulate)
        else:
            self.rotate(target_angle, speed=speed, debug_info=debug_info, simulate=simulate)

    def go_to(self, point: Point, linear_velocity = 0.2, angular_velocity = 0.5, debug_info: bool = False):
        distance = self.robot_pos.distance(point)
        if debug_info: print("DIST", distance)

        move_angle = self.robot_pos.relative_angle(point)

        turn_start = normalize_angle(move_angle - self.robot_pos.angle)
        if debug_info: 
            print("TEST", point.angle, move_angle, turn_start)
            input("PRESS ANY KEY...")
        # rotate for diagonal
        self.turn(turn_start, speed=angular_velocity, debug_info=debug_info)
        # go
        if debug_info: input("PRESS ANY KEY...")
        self.go(distance, set_speed=linear_velocity, debug_info=debug_info)
        # calculate a angle difference
        turn_end = normalize_angle(point.angle - move_angle)
        if debug_info:
            print("TEST2", turn_end, "Point", point.angle, move_angle)
            input("PRESS ANY KEY...")
        self.turn(turn_end, speed=angular_velocity, debug_info=debug_info)
        
    def get_objects_from_camera(self, debug_info: bool = False) -> list:
        # wait for rgb image
        self.turtle.wait_for_rgb_image()
        rgb_img = self.turtle.get_rgb_image()
        all_objects = find_ball.find_objects(rgb_img)
        # wait for point cloud find position of each object
        if debug_info: find_ball.show_objects(rgb_img, all_objects, "Objects", True)
        self.turtle.wait_for_point_cloud()
        pc = self.turtle.get_point_cloud()
        for o in all_objects:
            o.assign_xy(pc)
        return all_objects
    
    def scan_environment(self, robot_map: Map, max_angle = 2*np.pi, big = np.pi/6, small = np.pi/8, debug_info: bool = False) -> None:
        angle = 0
        while angle < max_angle and not self.turtle.is_shutting_down():
            if debug_info: print(f"DOING SCAN for angle {angle}")
            objects = self.get_objects_from_camera()
                
            if not objects:
                if debug_info: print("NOT FOUND -> ROTATE")
                self.rotate(big, speed=0.5)
                angle += big
                continue

            if debug_info: print("ALL OBJECTS:", objects)
            for obj in objects:
                robot_pos = self.position
                robot_angle = self.angle
                if debug_info: print("ROBOT POSITION:", robot_pos, robot_angle)
                robot_map.add_object(obj, robot_pos, True)
            if debug_info: print("\tSHOWING OBJECT")

            # all objects were scanned and kick position can be determined
            if robot_map.has_all or has_all(objects):
                break

            self.rotate(small)
            angle += small

    def center_ball(self, center = 335, offset = 10, debug_info: bool = False) -> None:
        while not self.turtle.is_shutting_down():
            all_objects_ = self.get_objects_from_camera()
            ball = list(filter(lambda x: x.o_type == find_ball.RigidType.BALL, all_objects_))

            if ball:
                if debug_info: print("---------\n", ball)
                ball = ball[0]
            else:
                self.turtle.cmd_velocity(angular=0.5)
                continue

            if center - offset <= ball.im_p.x <= center + offset:
                break
            elif ball.im_p.x > center:
                if debug_info: print("RIGHT -> SPEED: ", 0.4)
                self.turtle.cmd_velocity(angular=-0.4)
            else:
                if debug_info: print("LEFT-> SPEED: ", 0.4)
                self.turtle.cmd_velocity(angular=0.4)

            self.rate.sleep()


# positive angle -> left
# negative -> right
