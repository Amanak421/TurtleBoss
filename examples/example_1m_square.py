"""
Simple move test. Go around 1 m square.
"""


from robot import Robot
from robolab_turtlebot import Turtlebot, sleep, Rate
from math import pi


if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(50)

    test = Robot(turtle, rate)
    test.go(1)
    test.rotate(pi/2)
    test.go(1)
    test.rotate(pi/2)
    test.go(1)
    test.rotate(pi/2)
    test.go(1)
    test.rotate(pi/2)
