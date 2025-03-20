import sys
from math import pi
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
import find_ball
from mapping import Map
from movement import Move
from geometry import Point

def scan(turtle):
    turtle.wait_for_rgb_image()
    rgb_img = turtle.get_rgb_image()
    all_objects = find_ball.find_objects(rgb_img)
    # find position of each object
    pc = turtle.get_point_cloud()
    for o in all_objects:
        o.assign_xy(pc)
    find_ball.show_objects(rgb_img, all_objects, "Objects", True)
    # find_ball.show_objects(rgb_img, [], "Objects", True)
    return all_objects

if __name__ == "__main__":
    turtle_ = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle_.play_sound(1)
    sleep(0.3)
    rate = Rate(50)
    robot_move = Move(turtle_, rate)
    robot_move.reset()
    robot_map = Map()
    input("START ROBOT BY PRESSING KEY")
    print("ROBOT STARTED")
    angle = 0
    while angle < 4 * pi:
        print(f"DOING SCAN for angle {angle}")
        objects = scan(turtle_)
            
        if not objects:
            print("NOT FOUND -> ROTATE")
            robot_move.rotate(pi/6, speed=0.7)
            angle += pi/6
            continue

        print("ALL OBJECTS:", objects)
        for obj in objects:
            robot_pos = robot_move.xy
            robot_angle = robot_move.angle
            print("ROBOT POSITION:", robot_pos, robot_angle)
            robot_map.add_object(obj, robot_pos, robot_angle, True)
        print("\tSHOWING OBJECT")
        # robot_map.show(show_all=True, show_merged=False, robot_pos=robot_move.getPosition())

        robot_move.rotate(pi/12)
        angle += pi/12

    robot_map.show(show_all=True, show_merged=True, debug_info=True)