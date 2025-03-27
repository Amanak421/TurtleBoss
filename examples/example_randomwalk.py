import cv2
from enum import Enum
import numpy as np
import time
from robolab_turtlebot import Turtlebot

TRAVEL_TIME = 10

class ActionType(Enum):
    MOVE = 1
    ROTATE = 2

running = True
active = True


def make_random_move(turtle, linear_vel=0.2, angular_vel=0.3):
    print('Waiting for point cloud...')
    turtle.wait_for_point_cloud()
    direction = None
    print('First point cloud received...')

    start_time = time.time()
    while time.time() - start_time < TRAVEL_TIME:
        pc = turtle.get_point_cloud()

        if pc is None:
            print('No point cloud')
            continue

        # mask out floor and too far points
        mask = pc[:, :, 1] < 0.2
        mask = np.logical_and(mask, pc[:, :, 2] < 3.0)

        # empty image
        image = np.zeros(mask.shape)

        # assign depth i.e. distance to image
        image[mask] = np.int8(pc[:, :, 2][mask] / 3.0 * 255)
        im_color = cv2.applyColorMap(255 - image.astype(np.uint8), cv2.COLORMAP_JET)


        # check obstacle
        mask = np.logical_and(mask, pc[:, :, 1] > -0.2)
        data = np.sort(pc[:, :, 2][mask])

        state = ActionType.MOVE
        if data.size > 50:
            dist = np.percentile(data, 10)
            if dist < 0.6:
                state = ActionType.ROTATE

        # command velocity
        if active and state == ActionType.MOVE:
            turtle.cmd_velocity(linear=linear_vel)
            direction = None

        # obstacle based rotation
        elif active and state == ActionType.ROTATE:
            if direction is None:
                direction = np.sign(np.random.rand() - 0.5)
            turtle.cmd_velocity(angular=direction*angular_vel)




if __name__ == "__main__":
    turtle = Turtlebot(pc=True)
    make_random_move(turtle)
