import find_ball
import cv2
from robolab_turtlebot import Turtlebot, sleep


if __name__ == "__main__":
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    window_ = "RGB all objects"
    cv2.namedWindow(window_)
    while not turtle.is_shutting_down():
        print("________________")
        turtle.wait_for_rgb_image()
        rgb_img_ = turtle.get_rgb_image()
        all_objects_ = find_ball.find_objects(rgb_img_)
        print(*all_objects_, sep="\n")

        ball = list(filter(lambda x: x.o_type == find_ball.RigidType.BALL, all_objects_))
        if ball:
            ball = ball[0]
            pc = turtle.get_point_cloud()
            if not pc:
                print('No point cloud')
                continue
            else:
                print("yx", pc[ball.y][ball.x])
                print("xy", pc[ball.x][ball.y])

        find_ball.show_objects(rgb_img_, all_objects_, window_, wait=True)

    cv2.destroyAllWindows()

