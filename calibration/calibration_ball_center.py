from robot import Robot
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from math import pi



if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle.play_sound(1)
    sleep(0.3)
    rate = Rate(50)

    test = Robot(turtle, rate)
    test.reset()
    
    while not turtle.is_shutting_down():
        center, offset = (int(x) for x in input("CENTER, OFFSET: ").split(" ")[:2])
        test.center_ball(center=center, offset=offset)
