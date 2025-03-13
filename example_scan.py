from movement import Move
import find_ball
import sys
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from math import pi
from transform import Map

def scan(turtle):
    turtle.wait_for_rgb_image()
    rgb_img_ = turtle.get_rgb_image()
    all_objects_ = find_ball.find_objects(rgb_img_)
    # find position of each object

    return all_objects_

if __name__ == "__main__":
    turtle_ = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle_.play_sound(1)
    sleep(0.3)
    rate = Rate(10)
    robot_move = Move(turtle_, rate, False)
    robot_move.reset()
    robot_map = Map()
    input()

    last_find = False
    for i in range(1, 13):
        objects = scan(turtle_)

        if not objects and last_find:
            break
        elif not objects:
            robot_move.rotate(pi/6)
            continue

        for obj in objects:
            robot_pos = robot_move.getPosition()[:2]
            robot_angle = robot_move.getPosition()[2]
            robot_map.add_object(obj, robot_pos, robot_angle)
        robot_map.show(show_all=True, show_merged=False)

        robot_move.rotate(pi/6)
        last_find = True

    robot_map.show(show_all=True, show_merged=True)
        