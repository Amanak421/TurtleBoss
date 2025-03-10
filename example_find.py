from movement import Move
import find_ball
import sys
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from math import pi

if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(10)
    test = Move(turtle, rate, True)
    input()
    offset = 20
    center = 320

    while not turtle.is_shutting_down():
        turtle.wait_for_rgb_image()
        rgb_img_ = turtle.get_rgb_image()
        all_objects_ = find_ball.find_objects(rgb_img_)
        ball = list(filter(lambda x: x.o_type == find_ball.RigidType.BALL, all_objects_))[0]
        if center - offset <= ball.y <= center + offset:
            test.go(0.5)
        elif ball.y > center:
            test.rotate(0.3)
        else:
            test.rotate(-0.3)
