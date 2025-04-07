"""Robot control module."""


import sys

import numpy as np
from geometry import Point, normalize_angle
import find_ball
from mapping import Map, has_all
from constants import (LINEAR_CORRECTION, ANGULAR_CORRECTION, POSITION_NAMES,
                       STATE_NAMES, BASE_POSITION, LINEAR_EPSILON,
                       ANGULAR_EPSILON, MIN_LINEAR_VELOCITY,
                       MAX_LINEAR_VELOCITY, MIN_ANGULAR_VELOCITY,
                       MAX_ANGULAR_VELOCITY, LINEAR_KP, LINEAR_KD, ANGULAR_KP,
                       ANGULAR_KD)


class Robot:
    """Robot object."""

    def __init__(self, turtle: any, rate: any,
                 sleep_func: any = lambda _: None) -> None:
        self.robot_pos = BASE_POSITION

        self.kick_ball = False

        self.bumped = False
        self.button = False

        self.turtle = turtle
        self.rate = rate
        self.sleep_func = sleep_func

        turtle.register_bumper_event_cb(self.bumper_cb)
        turtle.register_button_event_cb(self.button_cb)

    def __repr__(self) -> str:
        """Return string representation of object."""
        return (f"X: {self.robot_pos.x}, Y: {self.robot_pos.y}, "
                f"ANGLE: {self.angle}\t")

    def __str__(self) -> str:
        """Return string representation of object."""
        return self.__repr__()

    @property
    def position(self) -> Point:
        """
        Get position of the robot.

        :return: Position of the robot
        """
        return self.robot_pos

    @property
    def xya(self) -> np.ndarray:
        """
        Get position of the robot.

        :return: x, y coordinates and angle
        """
        return self.robot_pos.xya

    @property
    def xy(self) -> np.ndarray:
        """
        Get position of the robot.

        :return: x, y coordinates
        """
        return self.robot_pos.xy

    @property
    def angle(self) -> float:
        """
        Get the angle of the robot.

        :return: angle (rotation from base position)
        """
        return self.robot_pos.angle

    def bumper_cb(self, msg: any) -> None:
        """Bumper callback."""
        bumper = POSITION_NAMES[msg.bumper]
        state = STATE_NAMES[msg.state]
        print(f"{bumper} bumper {state}")
        print("Bumped! -> Emergency stop!")
        self.bumped = True

    def button_cb(self, msg: any) -> None:
        """Button callback."""
        button = POSITION_NAMES[msg.button]
        state = STATE_NAMES[msg.state]
        print(f"{button} button {state}")
        self.button = True

    def check_bumper(self) -> None:
        """Stop the robot (and its program) if bumped."""
        if self.bumped and self.kick_ball:
            self.turtle.cmd_velocity()
            self.sleep_func(2)
            self.turtle.play_sound(5)
            sys.exit(66)
        elif self.bumped:
            self.turtle.cmd_velocity()
            sys.exit(66)

    def reset(self) -> None:
        """Reset data."""
        self.robot_pos = BASE_POSITION
        self.turtle.reset_odometry()
        self.turtle.wait_for_odometry()

    def reset_odometry(self) -> None:
        """Odometry reset."""
        self.turtle.reset_odometry()
        self.turtle.wait_for_odometry()

    def update_odometry_linear(self, x: float) -> None:
        """
        Call this after going forward (or backward) to update internal data.

        :param x: movement difference
        """
        self.robot_pos = self.robot_pos + Point(x * self.robot_pos.cos,
                                                x * self.robot_pos.sin)

    def update_odometry_angular(self, angle: float) -> None:
        """
        Call this after rotating to update internal data.

        :param angle: rotation difference
        """
        self.robot_pos.add_angle(angle)

    def get_odometry_angle(self, use_correction: bool = True) -> float:
        """
        Angle getter.

        :param use_correction: boolean for using predefined correction
        :return: angle
        """
        if use_correction:
            return self.turtle.get_odometry()[2] * ANGULAR_CORRECTION
        else:
            return self.turtle.get_odometry()[2]

    def get_odometry_x(self, use_correction: bool = True) -> float:
        """
        Directional move getter.

        :param use_correction: boolean for using predefined correction
        :return: x move
        """
        if use_correction:
            return self.turtle.get_odometry()[0] * LINEAR_CORRECTION
        else:
            return self.turtle.get_odometry()[0]

    def estimate_position(self) -> Point:
        """
        Estimate position with available odometry data.

        :return: newly estimated position
        """
        x, _, angle = self.turtle.get_odometry()
        return self.robot_pos + Point(x * self.robot_pos.cos,
                                      x * self.robot_pos.sin,
                                      normalize_angle(self.robot_pos.angle
                                                      + angle))

    def go(self,
           length: float,
           set_speed: float = None,
           stop: bool = True,
           simulate: bool = False,
           use_correction: bool = True,
           debug_info: bool = False) -> None:
        """
        Directional move with PD regulator.

        :param length: directional move length
        :param set_speed: desired speed
        :param stop: boolean for hard brake (True) or soft stop (False)
        :param simulate: boolean for virtual setup during debug
        :param use_correction: boolean for using predefined correction
        :param debug_info: boolean for debug
        """
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
            distance = self.get_odometry_x(use_correction=use_correction)

            error = length - distance
            if abs(error) < LINEAR_EPSILON or self.turtle.is_shutting_down():
                break

            if debug_info:
                print(f"{self.estimate_position()}")

            regulator = LINEAR_KP * error + LINEAR_KD * (error - last_error)
            speed = min(max(regulator, MIN_LINEAR_VELOCITY),
                        MAX_LINEAR_VELOCITY)
            if set_speed is not None:
                speed = set_speed

            self.turtle.cmd_velocity(linear=speed)
            self.check_bumper()
            self.rate.sleep()

        if stop:
            self.turtle.cmd_velocity()

        self.turtle.wait_for_odometry()
        real_distance = self.get_odometry_x(use_correction=use_correction)

        if debug_info:
            print("UPDATING ODOMETRY BY DISTANCE: ", real_distance)
        self.update_odometry_linear(real_distance)

    def go_until(self, speed: float = 0.3) -> None:
        """
        No stoppin' now! (well, except for bumping...).

        :param speed: desired move speed
        """
        self.turtle.cmd_velocity(linear=speed)
        self.check_bumper()
        self.rate.sleep()

    def kick(self, target_distance: float, speed: float = 1.5) -> None:
        """
        Kick the ball. Should be run only from the Kick position.

        :param target_distance: distance corresponding to Kick position
        :param speed: move speed
        """
        self.reset_odometry()
        self.kick_ball = True

        # move forward until desired length is hit
        while True:
            distance = self.get_odometry_x()
            if distance > target_distance or self.turtle.is_shutting_down():
                break
            self.check_bumper()
            self.turtle.cmd_velocity(linear=speed)
            self.rate.sleep()

        self.turtle.cmd_velocity()
        self.kick_ball = False

    def rotate(self,
               target_angle: float,
               set_speed: float = None,
               stop: bool = True,
               simulate: bool = False,
               use_correction: bool = True,
               debug_info: bool = False) -> None:
        """
        Rotational move with PD regulator.

        :param target_angle: rotational move angle
        :param set_speed: desired speed
        :param stop: boolean for hard brake (True) or soft stop (False)
        :param simulate: boolean for virtual setup during debug
        :param use_correction: boolean for using predefined correction
        :param debug_info: boolean for debug
        """
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
            angle = self.get_odometry_angle(use_correction=use_correction)

            error = abs(target_angle) - abs(angle)
            if debug_info:
                print("ROT ERROR", error)
            if abs(error) < ANGULAR_EPSILON or self.turtle.is_shutting_down():
                break

            if debug_info:
                print(self.estimate_position())

            regulator = ANGULAR_KP * error + ANGULAR_KD * (error - last_error)
            speed = min(max(regulator, MIN_ANGULAR_VELOCITY),
                        MAX_ANGULAR_VELOCITY)
            if set_speed:
                speed = set_speed

            self.turtle.cmd_velocity(angular=dir_coef * speed)
            self.check_bumper()
            self.rate.sleep()

        if stop:
            self.turtle.cmd_velocity()

        self.turtle.wait_for_odometry()
        real_angle = self.get_odometry_angle(use_correction=use_correction)

        if debug_info:
            print("UPDATING ODOMETRY BY ANGLE: ",
                  real_angle, "FINAL ERROR:",
                  target_angle - real_angle)
        self.update_odometry_angular(real_angle)

    def rotate_until(self, speed: float = 0.5) -> None:
        """
        No stoppin' now! (well, except for bumping...).

        :param speed: desired rotate speed
        """
        self.turtle.cmd_velocity(angular=speed)
        self.check_bumper()
        self.rate.sleep()

    def turn(self,
             target_angle: float,
             set_speed: float = 0.5,
             debug_info: bool = False,
             simulate: bool = False) -> None:
        """
        Ensure correct angle manipulation while rotating.

        :param target_angle: angle to turn
        :param set_speed: desired move speed
        :param debug_info: boolean for debug
        :param simulate: boolean for virtual setup during debug
        """
        if abs(target_angle) > (7 / 8) * np.pi:
            self.rotate(target_angle / 2, set_speed=set_speed,
                        debug_info=debug_info, simulate=simulate)
            self.rotate(target_angle / 2, set_speed=set_speed,
                        debug_info=debug_info, simulate=simulate)
        else:
            self.rotate(target_angle, set_speed=set_speed,
                        debug_info=debug_info, simulate=simulate)

    def go_to(self, point: Point, debug_info: bool = False) -> None:
        """
        Move to (x, y).

        :param point: (x, y) point
        :param debug_info: boolean for debug
        """
        distance = self.robot_pos.distance(point)
        if debug_info:
            print("DIST", distance)

        move_angle = self.robot_pos.relative_angle(point)

        turn_start = normalize_angle(move_angle - self.robot_pos.angle)
        if debug_info:
            print("TEST", point.angle, move_angle, turn_start)
            input("PRESS ANY KEY...")
        # rotate for diagonal
        self.turn(turn_start, debug_info=debug_info)

        # go
        if debug_info:
            input("PRESS ANY KEY...")
        self.go(distance, debug_info=debug_info)

        # calculate a angle difference
        turn_end = normalize_angle(point.angle - move_angle)
        if debug_info:
            print("TEST2", turn_end, "Point", point.angle, move_angle)
            input("PRESS ANY KEY...")
        self.turn(turn_end, debug_info=debug_info)

    def get_objects_from_camera(self, debug_info: bool = False) -> list:
        """
        Save all visible objects.

        :param debug_info: boolean for debug
        :return: list of all visible objects
        """
        # wait for rgb image
        self.turtle.wait_for_rgb_image()
        rgb_img = self.turtle.get_rgb_image()
        all_objects = find_ball.find_objects(rgb_img)
        # wait for point cloud find position of each object
        if debug_info:
            find_ball.show_objects(rgb_img, all_objects, "Objects", True)
        self.turtle.wait_for_point_cloud()
        pc = self.turtle.get_point_cloud()
        for o in all_objects:
            o.assign_xy(pc)
        return all_objects

    def scan_environment(self,
                         robot_map: Map,
                         max_angle: float = 2 * np.pi,
                         big: float = np.pi / 6,
                         small: float = np.pi / 8,
                         debug_info: bool = False) -> bool:
        """
        Scan objects around 360 ° or until or expected objects are found.

        :param robot_map: Map with internal data
        :param max_angle: 2pi for full rotation
        :param big: angle to rotate if there are no objects on the camera
        :param small: angle to rotate if there are some objects on the camera
        :param debug_info: boolean for debug
        :return: list of all seen objects during the scan
        """
        angle = 0
        while angle < max_angle and not self.turtle.is_shutting_down():
            if debug_info:
                print(f"DOING SCAN for angle {angle}")
            objects = self.get_objects_from_camera(debug_info=debug_info)

            if not objects:
                if debug_info:
                    print("NOT FOUND -> ROTATE")
                self.rotate(big)
                angle += big
                continue

            if debug_info:
                print("ALL OBJECTS:", objects)
            for obj in objects:
                robot_pos = self.position
                robot_angle = self.angle
                if debug_info:
                    print("ROBOT POSITION:", robot_pos, robot_angle)
                robot_map.add_object(obj, robot_pos, debug_info)
            if debug_info:
                print("\tSHOWING OBJECT")

            # all objects were scanned and kick position can be determined
            if robot_map.has_all or has_all(objects):
                return True

            self.rotate(small)
            angle += small

        return False

    def center_ball(self,
                    center: int = 350,
                    offset: int = 10,
                    debug_info: bool = False) -> None:
        """
        Set correctly in front of the ball.

        :param center: center of the screen in px
        :param offset: offset of the camera in px
        :param debug_info: boolean for debug
        """
        while not self.turtle.is_shutting_down():
            all_objects_ = self.get_objects_from_camera()
            ball = list(filter(lambda x: x.o_type ==
                               find_ball.RigidType.BALL, all_objects_))

            if ball:
                if debug_info:
                    print("---------\n", ball)
                ball = ball[0]
            else:
                self.turtle.cmd_velocity(angular=0.5)
                continue

            if center - offset <= ball.im_p.x <= center + offset:
                break
            elif ball.im_p.x > center:
                if debug_info:
                    print("RIGHT -> SPEED: ", 0.4)
                self.turtle.cmd_velocity(angular=-0.4)
            else:
                if debug_info:
                    print("LEFT-> SPEED: ", 0.4)
                self.turtle.cmd_velocity(angular=0.4)

            self.rate.sleep()


# positive angle -> left
# negative -> right
