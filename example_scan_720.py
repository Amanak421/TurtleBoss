import sys
from math import pi
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
import find_ball
from mapping import Map
from movement import Move
from geometry import Point
from rigidobject import RigidObject, RigidType

def scan(turtle):
    turtle.wait_for_rgb_image()
    rgb_img = turtle.get_rgb_image()
    all_objects = find_ball.find_objects(rgb_img)
    # find position of each object
    pc = turtle.get_point_cloud()
    for o in all_objects:
        o.assign_xy(pc)
    # find_ball.show_objects(rgb_img, all_objects, "Objects", True)
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

    #quick first scan
    angle = 0
    last_objects = None
    #while angle < 2*pi:
    #    print(f"DOING SCAN for angle {angle}")
    #    objects = scan(turtle_)
    #        
    #    if not objects and not last_objects:
    #        print("NOT FOUND -> ROTATE")
    #        robot_move.rotate(pi/3, speed=0.7)
    #        angle += pi/3
    #        continue
    #    elif not objects and last_objects:
    #        print("START ROTATING BACK")
    #        break
#
    #    print("ALL OBJECTS:", objects)
    #    for obj in objects:
    #        robot_pos = robot_move.position
    #        robot_angle = robot_move.angle
    #        print("ROBOT POSITION:", robot_pos, robot_angle)
    #        if obj.o_type == RigidType.BALL or obj.o_type == RigidType.POLE:
    #            last_objects = obj
    #    print("\tSHOWING OBJECT")
    #    # robot_map.show(show_all=True, show_merged=False, robot_pos=robot_move.getPosition())
#
    #    robot_move.rotate(pi/3)
    #    angle += pi/3
#
    #robot_move.rotate(-pi/3)
    robot_move.reset()
    # usable scan
    angle = 0
    while angle < 2*pi:
        print(f"DOING SCAN for angle {angle}")
        objects = scan(turtle_)
            
        if not objects:
            print("NOT FOUND -> ROTATE")
            robot_move.rotate(-pi/6, speed=0.5)
            angle += pi/6
            continue

        print("ALL OBJECTS:", objects)
        for obj in objects:
            robot_pos = robot_move.position
            robot_angle = robot_move.angle
            print("ROBOT POSITION:", robot_pos, robot_angle)
            robot_map.add_object(obj, robot_pos, True)
        print("\tSHOWING OBJECT")
        # robot_map.show(show_all=True, show_merged=False, robot_pos=robot_move.getPosition())

        robot_move.rotate(-pi/8)
        angle += pi/8

    robot_map.show(show_all=True, show_merged=True, debug_info=True)

    ball = robot_map.ball

    kick_pos = robot_map.determine_kick_pos(dist=0.9)
    #midpoint = robot_move.midpoint(kick_pos[0], kick_pos[1], *ball[0].position)
    print("MOVING TO POSITION: ", kick_pos)
    robot_map.show(show_all=False, show_merged=True, robot_pos=robot_move.position, kick_pos=kick_pos, debug_info=True)
    input("GO TO POSITION -> PRESS KEY")
    robot_move.go_to(kick_pos, linear_velocity=0.4, angular_velocity=0.45)

    offset = 40
    center = 335

    print("INIT KICK MODE")
    input("PRESS ANY KEY TO CONTINUE")

    while not turtle_.is_shutting_down():
        turtle_.wait_for_rgb_image()
        rgb_img_ = turtle_.get_rgb_image()
        all_objects_ = find_ball.find_objects(rgb_img_)
        ball = list(filter(lambda x: x.o_type == find_ball.RigidType.BALL, all_objects_))

        print("---------")
        print(ball)

        if ball:
            ball = ball[0]
        else:
            turtle_.cmd_velocity(angular=0.5)
            continue

        pc_ = turtle_.get_point_cloud()
        if pc_ is None:
            print('No point cloud')
            continue

        if center - offset <= ball.im_p.x <= center + offset:
            if pc_[ball.im_p.x][ball.im_p.y][2] < 0.60:
                input("READY TO KICK -> CONFIRM")
                robot_move.kick(0.4, speed=1)
                turtle_.cmd_velocity()
                sleep(1)
                turtle_.play_sound(5)
                print("PROGRAM ENDED")
                break
            else:
                turtle_.cmd_velocity(linear=0.2)

            
        elif ball.im_p.x > center:
            print("RIGHT -> SPEED: ", (max((abs(center - ball.im_p.x)/640)*0.9, 0.4)))
            turtle_.cmd_velocity(angular=-(max((abs(center - ball.im_p.x)/640)*1.5, 0.4)))
        else:
            print("LEFT-> SPEED: ", (max((abs(center - ball.im_p.x)/640)*0.9, 0.4)))
            turtle_.cmd_velocity(angular=(max((abs(center - ball.im_p.x)/640)*1.5, 0.4)))