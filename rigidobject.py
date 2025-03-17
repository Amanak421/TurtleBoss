from enum import Enum
import numpy as np


RADIUS_POLE = 0.025
RADIUS_BALL = 0.11


class ColorType(Enum):
    YELLOW = 1
    BLUE = 2
    GREEN = 3
    RED = 4


class RigidType(Enum):
    BALL = 1
    POLE = 2
    OBST = 3


class RigidObject:
    def __init__(self, x, y, w, h, o_type: RigidType, c_type: ColorType):
        self.x = 0  # x_pc
        self.y = 0  # y_pc
        self.im_x = x  # x_rgb
        self.im_y = y  # y_rgb
        self.w = w
        self.h = h
        self.o_type = o_type
        self.c_type = c_type

    def __repr__(self):
        return f"{self.c_type.name} {self.o_type.name} on {self.im_x}, {self.im_y} at {self.x}, {self.y}\t"

    def __str__(self):
        return self.__repr__()

    @property
    def position(self):
        return np.array([self.x, self.y])

    def set_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def assign_xy(self, pc):
        """
        Assign x, y data from point cloud.
        :param pc: Point cloud
        :return:
        """
        r = (RADIUS_BALL if self.o_type == RigidType.BALL else RADIUS_POLE)
        vector = pc[self.im_y][self.im_x][0], pc[self.im_y][self.im_x][2]
        norm = np.linalg.norm(vector)
        self.x = pc[self.im_y][self.im_x][2]  # + r * vector[0] / norm
        self.y = -pc[self.im_y][self.im_x][0]  # + r * vector[1] / norm

        print("TEST PRINT X Y: ", self.x, self.y)
