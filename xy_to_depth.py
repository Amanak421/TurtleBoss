import find_ball
import cv2
from robolab_turtlebot import Turtlebot, sleep

"""def load_pc(filename):
    data = scipy.io.loadmat(filename)
    pc = data["point_cloud"]
    return pc"""




if __name__ == "__main__":
    # pc_ = load_pc(f"test_data/test_y{1}.mat")
    turtle = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    window_ = "RGB all objects"
    cv2.namedWindow(window_)
    for img_index in range(5):
        turtle.wait_for_rgb_image()
        rgb_img_ = turtle.get_rgb_image()
        all_objects_ = find_ball.find_objects(rgb_img_)
        print(*all_objects_, sep="\n")
        find_ball.show_objects(rgb_img_, all_objects_, window_, wait=True)
    cv2.destroyAllWindows()

