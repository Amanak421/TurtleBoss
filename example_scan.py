import sys
from math import pi
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
import find_ball
from mapping import Map
from movement import Move

def scan(turtle):
    turtle.wait_for_rgb_image()
    rgb_img = turtle.get_rgb_image()
    all_objects = find_ball.find_objects(rgb_img)
    # find position of each object
    pc = turtle.get_point_cloud()
    for o in all_objects:
        o.assign_xy(pc)
    find_ball.show_objects(rgb_img, all_objects, "Objects", True)
    find_ball.show_objects(rgb_img, [], "Objects", True)
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
    first_found = True
    ball_detected = False

    while True:
        print(f"DOING SCAN")
        objects = scan(turtle_)

        # ball on image

        ball = list(filter(lambda x: x.o_type == find_ball.RigidType.BALL, objects))
        if len(ball) == 1 and ball_detected == False:
            robot_move.reset()
            if 50 <= ball[0].im_x <= 430:
                robot_map.add_object(ball[0], robot_move.getPosition()[:2], robot_move.getPosition()[2], True)
                robot_move.reset()
                ball_detected = True

        poles = list(filter(lambda x: x.o_type == find_ball.RigidType.POLE, objects))
        if ball_detected and len(poles) == 2:
            for p in poles:
                robot_map.add_object(p, robot_move.getPosition()[:2], robot_move.getPosition()[2], True)
            break

        robot_move.rotate(pi/12)



    kick_pos = robot_map.determine_kick_pos()
    print("MOVING TO POSITION: ", kick_pos)
    robot_map.show(show_all=False, show_merged=True, robot_pos=robot_move.getPosition()[:2], kick_pos=kick_pos, debug_info=True)

    robot_move.go_to(*kick_pos, 0, linear_velocity=0.4, angular_velocity=0.45)


        