import sys
from math import pi
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
import find_ball
from mapping import Map, has_all
from movement import Move
from geometry import Point
from rigidobject import RigidObject, RigidType

if __name__ == "__main__":
    turtle_ = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle_.play_sound(1)
    sleep(0.3)
    rate = Rate(50)
    robot_move = Move(turtle_, rate)
    robot_move.reset()
    robot_map = Map(turtle_)
    input("START ROBOT BY PRESSING KEY")
    print("ROBOT STARTED")

    angle = 0
    last_objects = None
    robot_move.reset()
    # usable scan
    angle = 0
    while angle < 2*pi:
        print(f"DOING SCAN for angle {angle}")
        objects = robot_map.scan_environment()
            
        if not objects:
            print("NOT FOUND -> ROTATE")
            robot_move.rotate(pi/6, speed=0.5)
            angle += pi/6
            continue

        print("ALL OBJECTS:", objects)
        for obj in objects:
            robot_pos = robot_move.position
            robot_angle = robot_move.angle
            print("ROBOT POSITION:", robot_pos, robot_angle)
            robot_map.add_object(obj, robot_pos, True)
        print("\tSHOWING OBJECT")

        #all objects was scanned and kick position can be determined
        if robot_map.has_all or has_all(objects):
            break

        robot_move.rotate(pi/8)
        angle += pi/8

    ball = robot_map.ball
    kick_pos = robot_map.determine_kick_pos(dist=1)
    path = robot_map.routing(robot_pos, kick_pos)
    
    robot_map.show(show_all=False, show_merged=True, robot_pos=robot_move.position, kick_pos=kick_pos, debug_info=True)

    for p in path[1:]:


    robot_move.go_to(kick_pos, linear_velocity=0.4, angular_velocity=0.45)

    # get photo and get better position
    robot_map.reset()
    print(f"DOING SCAN for angle {angle}")
    objects = robot_map.scan_environment()
    
    if objects:
        print("ALL OBJECTS:", objects)
        for obj in objects:
            robot_pos = robot_move.position
            robot_angle = robot_move.angle
            print("ROBOT POSITION:", robot_pos, robot_angle)
            robot_map.add_object(obj, robot_pos, True)
        
        print("\tSHOWING OBJECT")
        robot_map.show(show_all=False, show_merged=True, robot_pos=robot_move.position, kick_pos=kick_pos, debug_info=True)
        
        kick_pos = robot_map.determine_kick_pos(dist=0.6)
        robot_move.go_to(kick_pos, linear_velocity=0.4, angular_velocity=0.45)

    offset = 40
    center = 335

    print("INIT KICK MODE")
    input("PRESS ANY KEY TO CONTINUE")

    while not turtle_.is_shutting_down():
        all_objects_ = robot_map.scan_environment()
        ball = list(filter(lambda x: x.o_type == find_ball.RigidType.BALL, all_objects_))

        if ball:
            ball = ball[0]
        else:
            turtle_.cmd_velocity(angular=0.5)
            continue

        print("---------")
        print(ball)

        if center - offset <= ball.im_p.x <= center + offset:
            #input("READY TO KICK -> CONFIRM")
            robot_move.kick(0.5, speed=1)
            turtle_.cmd_velocity()
            sleep(0.2)
            turtle_.play_sound(5)
            print("PROGRAM ENDED")
            break

        elif ball.im_p.x > center:
            print("RIGHT -> SPEED: ", (max((abs(center - ball.im_p.x)/640)*0.9, 0.4)))
            turtle_.cmd_velocity(angular=-(max((abs(center - ball.im_p.x)/640)*2, 0.4)))
        else:
            print("LEFT-> SPEED: ", (max((abs(center - ball.im_p.x)/640)*0.9, 0.4)))
            turtle_.cmd_velocity(angular=(max((abs(center - ball.im_p.x)/640)*2, 0.4)))

        rate.sleep()