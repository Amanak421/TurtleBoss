from movement import Move
import find_ball
import sys
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from math import pi
from transform import Map
from kick_pos import determine_kick_pos

def scan(turtle):
    turtle.wait_for_rgb_image()
    rgb_img = turtle.get_rgb_image()
    all_objects = find_ball.find_objects(rgb_img)
    # find position of each object
    pc = turtle.get_point_cloud()
    for o in all_objects:
        o.assign_xy(pc)
    #find_ball.show_objects(rgb_img, all_objects, "Objects", True)
    #find_ball.show_objects(rgb_img, [], "Objects", True)
    return all_objects

if __name__ == "__main__":
    turtle_ = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle_.play_sound(1)
    sleep(0.3)
    rate = Rate(10)
    robot_move = Move(turtle_, rate, False)
    robot_move.reset()
    robot_map = Map()
    input("START ROBOT BY PRESSING KEY")
    print("ROBOT STARTED")
    last_find = False
    for i in range(1, 8):
        print(f"DOING SCAN {i} OUT OF 12")
        objects = scan(turtle_)

        if not objects and last_find:
            print("ALL OBJECTS  FOUND -> BREAK")
            
        elif not objects:
            print("NOT FOUND -> ROTATE")
            robot_move.rotate(pi/6)
            continue

        print("ALL OBJECTS:", objects)
        for obj in objects:
            robot_pos = robot_move.getPosition()[:2]
            robot_angle = robot_move.getPosition()[2]
            print("ROBOT POSITION:", robot_pos, robot_angle)
            robot_map.add_object(obj, robot_pos, robot_angle)
        print("\tSHOWING OBJECT")
        #robot_map.show(show_all=True, show_merged=False, robot_pos=robot_move.getPosition())

        robot_move.rotate(pi/6)
        last_find = True

    robot_map.show(show_all=True, show_merged=True)

    poles = robot_map.get_poles()
    ball = robot_map.get_ball()

    kick_pos = determine_kick_pos(poles[0].position(), poles[1].position(), ball[0].position(), dist=0.5)
    print("MOVING TO POSITION: ", kick_pos)
    robot_map.show(show_all=False, show_merged=True, robot_pos=robot_move.getPosition(), kick_pos=kick_pos)

    robot_move.go_to(*kick_pos, linear_velocity=0.4, angular_velocity=0.45)

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

        pc = turtle_.get_point_cloud()
        if pc is None:
            print('No point cloud')
            continue

        if center - offset <= ball.im_x <= center + offset:
            print(pc[ball.y][ball.im_x])
            if pc[ball.im_y][ball.im_x][2] < 0.60:
                input("READY TO KICK -> CONFIRM")
                robot_move.go(0.4, 1)
                turtle_.cmd_velocity()
                sleep(1)
                turtle_.play_sound(5)
                print("PROGRAM ENDED")
                break
            else:
                turtle_.cmd_velocity(linear=0.2)

            
        elif ball.im_x > center:
            print("RIGHT -> SPEED: ", (max((abs(center - ball.im_x)/640)*0.9, 0.35)))
            turtle_.cmd_velocity(angular=-(max((abs(center - ball.im_x)/640)*1.5, 0.35)))
        else:
            print("LEFT-> SPEED: ", (max((abs(center - ball.im_x)/640)*0.9, 0.4)))
            turtle_.cmd_velocity(angular=(max((abs(center - ball.im_x)/640)*1.5, 0.4)))

        