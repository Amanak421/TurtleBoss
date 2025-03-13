import find_ball
import cv2
from robolab_turtlebot import Turtlebot, sleep

from find_ball import RigidType


def assign_xy(pc, ro: find_ball.RigidObject):
    """
    Assign x, y data from point cloud to a single RigidObject.
    :param pc: Point cloud
    :param ro: RigidObject
    :return:
    """
    if ro.o_type == RigidType.BALL:
        ro.x = pc[ro.im_y][ro.im_x][0]
        ro.y = pc[ro.im_y][ro.im_x][2]
    else:
        x_center = (ro.im_x + ro.w) / 2
        y_center = (ro.im_y + ro.h) / 2
        ro.x = pc[y_center][x_center][0]
        ro.y = pc[y_center][x_center][2]

    """
    robot_x
    """




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
            pc_ = turtle.get_point_cloud()
            if pc_ is None:
                print('No point cloud')
                continue
            else:
                print("yx", pc_[ball.y][ball.x])

        find_ball.show_objects(rgb_img_, all_objects_, window_, wait=True)

    cv2.destroyAllWindows()

