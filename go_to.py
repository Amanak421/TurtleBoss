from movement import Move
import sys
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from math import pi

if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(50)
    test = Move(turtle, rate, True)

    while True:
        inp = input(">> ")
        if inp == "e":
            break
        if inp == "r":
            test.reset()
        if inp == "p":
            print(f"Position: {test.getPosition()}")
        if inp.split(" ")[0] == "g":
            x, y, angle = [float(x) for x in inp.split(" ")[1:]]
            print(f"GO TO: {x} {y} {angle}")
            test.go_to(x, y, angle)
            print(f"Position: {test.getPosition()}")