"""Calibration of rotational move error constant."""

from math import pi

from robot import Robot
from robolab_turtlebot import Turtlebot, sleep, Rate


if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(50)

    test = Robot(turtle, rate)

    print("BEFORE MOVE:")
    before = test.xya
    print(test.position)
    print("MOVING...")

    test.rotate(pi)
    test.rotate(pi)
    test.rotate(pi)
    test.rotate(pi)

    print("ROBOT AFTER MOVE\n", test.position)
    robot_after = test.xya
    after = float(input("REAL AFTER MOVE: "))
    print("DIFFERENCE")
    print(robot_after - after)
    print("Correction constant:", 4 * pi / after)
