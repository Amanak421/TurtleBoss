from robolab_turtlebot import Turtlebot, sleep, Rate
from mapping import Map
from robot import Robot
from scipy.io import savemat
from datetime import datetime


if __name__ == "__main__":
    turtle_ = Turtlebot(rgb=True, depth=True, pc=True)
    sleep(2)
    turtle_.play_sound(1)
    sleep(0.3)
    rate = Rate(50)
    robot = Robot(turtle_, rate)
    robot.reset()
    robot_map = Map()

    while not turtle_.is_shutting_down():
        if robot.button:
            turtle_.play_sound(5)
            # get K, images, and point cloud -> copy from example scripts
            data = dict()
            data['K_rgb'] = turtle_.get_rgb_K()
            data['K_depth'] = turtle_.get_depth_K()
            data['image_rgb'] = turtle_.get_rgb_image()
            data['image_depth'] = turtle_.get_depth_image()
            data['point_cloud'] = turtle_.get_point_cloud()

            # save data to .mat file
            filename = (datetime.today().strftime("photos/%Y-%m-%d-%H-%M-%S") +
                        ".mat")
            savemat(filename, data)

            print(f"Data saved in {filename}")
            robot.button = False
