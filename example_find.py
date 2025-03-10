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
    test = Move(turtle, rate, False)
    input()
    offset = 40
    center = 320

    while not turtle.is_shutting_down():
        turtle.wait_for_rgb_image()
        rgb_img_ = turtle.get_rgb_image()
        all_objects_ = find_ball.find_objects(rgb_img_)
        ball = list(filter(lambda x: x.o_type == find_ball.RigidType.BALL, all_objects_))
        print("---------")
        print(ball)
        if ball:
            ball = ball[0]
        else:
            test.rotate(pi/10, speed=0.8)
            continue

        pc = turtle.get_point_cloud()
        if not pc:
            print('No point cloud')
            continue

        if center - offset <= ball.x <= center + offset:
            print(pc[ball.y][ball.x])
            """if pc[ball.y][ball.x][]:
                test.go()
            else:"""
            test.go(0.1)
        elif ball.x > center:
            test.rotate(-pi/20, speed=(min(abs(center - ball.x)/center, 0.3)))
        else:
            test.rotate(pi/20, speed=(min(abs(center - ball.x)/center, 0.3)))
