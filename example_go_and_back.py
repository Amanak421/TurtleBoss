# TODO depreciate or rename to an example
from movement import Move
import sys
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from math import pi
from geometry import Point, normalize_angle

if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(50)
    test = Move(turtle, rate)

    test.go(1)
    test.rotate(pi)
    test.go(1)
    test.rotate(pi)