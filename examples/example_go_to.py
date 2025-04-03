# TODO depreciate or rename to an example
from robot import Robot
from robolab_turtlebot import Turtlebot, sleep, Rate
from geometry import Point


if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(50)
    test = Robot(turtle, rate)

    while True:
        inp = input(">> ")
        if inp == "e":
            break
        if inp == "r":
            test.reset()
        if inp == "p":
            print(f"Position: {test.xya}")
        if inp.split(" ")[0] == "g":
            x, y, angle = [float(x) for x in inp.split(" ")[1:]]
            print(f"GO TO: {x} {y} {angle}")
            test.go_to(Point(x, y, angle), debug_info=True)
            print(f"Position: {test.xya}")
