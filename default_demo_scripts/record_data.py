from __future__ import print_function

from datetime import datetime

from robolab_turtlebot import Turtlebot, sleep

from scipy.io import savemat

# initialize turlebot
turtle = Turtlebot(rgb=True, depth=True, pc=True)

# sleep 2 set to receive images
sleep(2)

# get K, images, and point cloud
data = dict()
data['K_rgb'] = turtle.get_rgb_K()
data['K_depth'] = turtle.get_depth_K()
data['image_rgb'] = turtle.get_rgb_image()
data['image_depth'] = turtle.get_depth_image()
data['point_cloud'] = turtle.get_point_cloud()

# save data to .mat file
filename = datetime.today().strftime("%Y-%m-%d-%H-%M-%S") + ".mat"
savemat(filename, data)

print('Data saved in {}'.format(filename))
