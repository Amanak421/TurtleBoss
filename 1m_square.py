from movement import Move
import sys
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from math import pi



if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(10)

    test = Move(turtle, rate)
    print(test.getPosition())
    test.go(2, simulate=False, _print=True)
    print(test.getPosition())
    test.rotate(pi/2, simulate=False, _print=True)
    print(turtle.get_odometry())
    print(test.getPosition())
    test.rotate(pi/2, simulate=False, _print=True)
    print(turtle.get_odometry())
    test.go(2, simulate=False, _print=True)
    print(test.getPosition())
