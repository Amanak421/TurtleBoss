import sys
from math import sin, cos, atan2, sqrt, pi
import time
from visual import Visual

class Move:
    def __init__(self, turtle, rate, visual):
        self.WAIT_TIME = 0.1
        self.LINEAR_CORRECTION = 0.98  #0.96
        self.ANGULAR_CORRECTION = 1.04

        self.BUMPER_NAMES = ['LEFT', 'CENTER', 'RIGHT']
        self.STATE_NAMES = ['RELEASED', 'PRESSED']

        self.x = 0
        self.y = 0
        self.angle = 0

        self.turtle = turtle
        self.rate = rate

        self.visual = visual
        if visual:
            self.vis = Visual()
            self.vis.updateRobot(*self.getPosition())
            print("VIS START")
        else:
            self.vis = None

        turtle.register_bumper_event_cb(self.bumper_cb)

    def bumper_cb(self, msg):
        """Bumper callback."""
        bumper = self.BUMPER_NAMES[msg.bumper]
        state = self.STATE_NAMES[msg.state]
        print('{} bumper {}'.format(bumper, state))
        print("Bumped! -> Emergency stop!")
        sys.exit(66)

    def reset(self) -> None:
        self.x, self.y, self.angle = 0, 0, 0
        self.turtle.reset_odometry()

    def resetOdometry(self):
        self.turtle.reset_odometry()
        # wait for odometry reset
        time.sleep(self.WAIT_TIME)

    def updateOdometryLinear(self, x) -> None:
        self.x = self.x + x*cos(self.angle)
        self.y = self.y + x*sin(self.angle)

    def updateOdometryAngular(self, angle) -> None:
        self.angle = self.normalizeAngle(self.angle + angle)

    def estimatePosition(self, x, angle):
        return self.x + x*cos(self.angle), self.x + x*sin(self.angle), self.normalizeAngle(self.angle + angle)

    def getPosition(self):
        return self.x, self.y, self.angle

    def normalizeAngle(self, angle):
        return atan2(sin(angle), cos(angle))

    def go(self, length, speed = 0.3, _print = False, simulate=False) -> None:
        # reset robot odometry
        if simulate:
            self.updateOdometryLinear(length)
            return
        
        if length == 0:
            return

        self.resetOdometry()
        # move forward until desired length is hit
        while True:
            odometry = self.turtle.get_odometry()
            distance = odometry[0] * self.LINEAR_CORRECTION
            if distance > length or self.turtle.is_shutting_down():
                break
            if _print:
                print(self.estimatePosition(odometry[0], odometry[2]))
            self.turtle.cmd_velocity(linear=speed)
            self.rate.sleep()
        
        #self.turtle.cmd_velocity()
        self.updateOdometryLinear(self.turtle.get_odometry()[0] * self.LINEAR_CORRECTION)
        if self.visual:
            self.vis.updateRobot(*self.getPosition())

    def go_until(self, condition, speed = 0.3, _print = False):
        self.resetOdometry()
        # move forward until desired length is hit
        while True:
            odometry = self.turtle.get_odometry()
            distance = odometry[0] * self.LINEAR_CORRECTION
            if condition() or self.turtle.is_shutting_down():
                break
            if _print:
                print(self.estimatePosition(odometry[0], odometry[2]))
            self.turtle.cmd_velocity(linear=speed)
            self.rate.sleep()

    def angleCheck(self, angle, target_angle):
        return angle <= target_angle if target_angle > 0 else angle > target_angle

    def rotate(self, target_angle, speed = 0.5, _print = False, simulate=False):
        if simulate:
            self.updateOdometryAngular(target_angle)
            return

        if target_angle == 0:
            return
        
        dir_coef = 1
        if target_angle < 0:
            dir_coef = -1

        # reset robot odometry
        self.resetOdometry()
        count = 0
        # rotate until desired angle is hit
        while True:
            odometry = self.turtle.get_odometry()
            angle = odometry[2] * self.ANGULAR_CORRECTION
            if self.angleCheck(angle, target_angle) or self.turtle.is_shutting_down():
                break
            if _print:
                print(self.estimatePosition(odometry[0], odometry[2]))
            self.turtle.cmd_velocity(angular=dir_coef * speed)
            count+=1
            self.rate.sleep()


        #self.turtle.cmd_velocity()
        self.updateOdometryAngular(self.turtle.get_odometry()[2] * self.ANGULAR_CORRECTION)
        if self.visual:
            self.vis.updateRobot(*self.getPosition())

    def rotate_until(self, condition, speed = 0.5, _print = False):
        self.resetOdometry()

        while True:
            odometry = self.turtle.get_odometry()
            angle = odometry[2] * self.ANGULAR_CORRECTION
            if not condition() or self.turtle.is_shutting_down():
                break
            if _print:
                print(self.estimatePosition(odometry[0], odometry[2]))
            self.turtle.cmd_velocity(angular = speed)
            self.rate.sleep()


        #self.turtle.cmd_velocity()
        #self.updateOdometryAngular(self.turtle.get_odometry()[2] * self.ANGULAR_CORRECTION)
        if self.visual:
            self.vis.updateRobot(*self.getPosition())

    def turn(self, target_angle, speed = 0.5, _print = True, simulate=False):
        if abs(target_angle) > (7/8)*pi:
            self.rotate(target_angle/2, speed=speed, _print=_print, simulate=simulate)
            print("SECOND TURN")
            self.rotate(target_angle/2, speed=speed, _print=_print, simulate=simulate)
        else:
            self.rotate(target_angle, speed=speed, _print=_print, simulate=simulate)

    def go_to(self, x, y, angle, linear_velocity = 0.3, angular_velocity = 0.6):
        distance = sqrt((x - self.x)**2 + (y - self.y)**2)
        print("DIST", distance)
        move_angle = atan2(y - self.y, x - self.x)
        turn_start = self.normalizeAngle(move_angle - self.angle)
        print("TEST", angle, move_angle, turn_start)
        #rotate for diagonal
        self.turn(turn_start, speed=angular_velocity)
        #go
        self.go(distance, speed=linear_velocity)
        #calculate a angle difference
        turn_end = self.normalizeAngle(angle - move_angle)
        print("TEST2",turn_end)
        self.turn(turn_end, speed=angular_velocity)
