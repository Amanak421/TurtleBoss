from enum import Enum
import numpy as np
from geometry import Point


RADIUS_POLE = 0.025
RADIUS_BALL = 0.11


class ColorType(Enum):
    YELLOW = "yellow"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    BLACK = "black"


class RigidType(Enum):
    BALL = 1
    POLE = 2
    OBST = 3


class RigidObject:
    def __init__(self, x, y, w, h, o_type: RigidType,
                 c_type: ColorType = None):
        self.p = Point(0, 0)  # (x,y)_pc
        self.im_p = Point(x, y)  # (x,y)_rgb
        self.w = w
        self.h = h
        self.o_type = o_type
        if c_type is None:
            self.c_type = {
                RigidType.BALL: ColorType.YELLOW,
                RigidType.POLE: ColorType.BLUE,
                RigidType.OBST: ColorType.RED,
            }.get(self.o_type, ColorType.BLACK)
        else:
            self.c_type = c_type

    def __repr__(self):
        return f"""{self.c_type.name} {self.o_type.name} on {self.im_p.xy[0]},
                    {self.im_p.xy[1]} at {self.p.xy[0]}, {self.p.xy[1]}\t"""

    def __str__(self):
        return self.__repr__()

    @property
    def color(self):
        """
        :return: Symbolic color for visualization
        """
        return self.c_type.value

    @property
    def position(self):
        """
        :return: Numpy-fied real-world coordinates x, y as Point
        """
        return self.p

    @property
    def xy(self):
        """
        :return: Numpy-fied real-world coordinates x, y as np.array
        """
        return self.p.xy

    @property
    def im_position(self):
        """
        :return: Numpy-fied image coordinates x, y
        """
        return self.im_p.xy

    def set_position(self, new_pos: Point):
        """
        Set real-world coordinates
        :param new_pos: Point(x, y)
        :return:
        """
        self.p = new_pos

    def assign_xy(self, pc):
        """
        Assign x, y data from point cloud.
        :param pc: Point cloud
        :return:
        """
        r = 0  # (RADIUS_BALL if self.o_type == RigidType.BALL else RADIUS_POLE)
        vector = (pc[self.im_p.xy[1]][self.im_p.xy[0]][0],
                  pc[self.im_p.xy[1]][self.im_p.xy[0]][2])
        norm = np.linalg.norm(vector)
        self.p.x = (pc[self.im_p.xy[1]][self.im_p.xy[0]][2] +
                    r * vector[0] / norm)
        self.p.y = (-pc[self.im_p.xy[1]][self.im_p.xy[0]][0] +
                    r * vector[1] / norm)
