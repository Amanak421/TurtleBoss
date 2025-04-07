"""Calibration for compensation of off-centered camera."""


from robot import Robot
from robolab_turtlebot import Turtlebot, sleep, Rate


if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(50)

    test = Robot(turtle, rate)
    test.reset()

    while not turtle.is_shutting_down():
        center, offset = (int(x) for x in
                          input("CENTER, OFFSET: ").split(" ")[:2])
        test.center_ball(center=center, offset=offset)
