"""
Geometry module with Point, Line and Segment.

Used primarily in mapping.py.
"""


from typing import Union

import numpy as np


def normalize_angle(angle: float) -> float:
    """
    Normalize given angle in radians to the range (-π, π].

    :param angle: angle to normalize
    :return: normalized angle
    """
    return np.arctan2(np.sin(angle), np.cos(angle))


class Point:
    """
    Vector representing a location of a certain point.

    Implemented basic arithmetic operations.
    """

    def __init__(self, x: float, y: float, angle: float = 0) -> None:
        """
        Create Point instance.

        :param x: x position
        :param y: y position
        :param angle: rotation of the vector
        """
        self.x = x
        self.y = y
        self.angle = angle

    def __repr__(self) -> str:
        """Return string representation of object."""
        return f"({self.x}, {self.y}, {self.angle})"

    def __str__(self) -> str:
        """Return string representation of object."""
        return self.__repr__()

    def __add__(self, point: 'Point'):
        """
        Add another point to itself.

        Angle is inherited from self.
        :param point: second Point
        """
        return Point(self.x + point.x, self.y + point.y, self.angle)

    def __sub__(self, point: 'Point'):
        """
        Subtract another point from itself.

        Angle is inherited from self.
        :param point: second Point
        """
        return Point(self.x - point.x, self.y - point.y, self.angle)

    def __mul__(self, factor: float):
        """
        Multiply point by a factor.

        Angle is untouched.
        :param factor: multiplication factor
        """
        if isinstance(factor, int):
            return Point(self.x * factor, self.y * factor, self.angle)
        else:
            return NotImplemented

    def __rmul__(self, factor: float):
        """Comitative multiplication."""
        return self.__mul__(factor)

    def __truediv__(self, divisor: float):
        """
        Define true division by a factor.

        Angle is untouched.
        :param factor: division factor
        """
        # Prevent division by zero
        if isinstance(divisor, (int, float)) and divisor != 0:
            return Point(self.x / divisor, self.y / divisor, self.angle)
        else:
            return NotImplemented

    def __rtruediv__(self, divisor: int):
        """Right true division not implemented."""
        return NotImplemented

    @property
    def xya(self) -> np.ndarray:
        """
        Get position of the point.

        :return: x, y coordinates and angle
        """
        return np.array((self.x, self.y, self.angle))

    @property
    def xy(self) -> np.ndarray:
        """
        Get position of the point.

        :return: x, y coordinates
        """
        return np.array((self.x, self.y))

    @property
    def sin(self) -> np.ndarray:
        """
        Get sin of the point angle.

        :return: sin of angle
        """
        return np.sin(self.angle)

    @property
    def cos(self) -> np.ndarray:
        """
        Get cos of the point angle.

        :return: cos of angle
        """
        return np.cos(self.angle)

    @property
    def homog_xy(self) -> np.ndarray:
        """
        Homogenize (x, y) -> (x, y, 1).

        :return: homogenous coordinates
        """
        return np.array((self.x, self.y, 1))

    def add_angle(self, angle: float) -> None:
        """
        Update angle by adding another one.

        :param angle: angle to add
        """
        self.angle = normalize_angle(self.angle + angle)

    def distance(self, point: 'Point') -> float:
        """
        Based on pythagorean theorem, calculate distance from a point.

        :param point: target point
        :return: distance from the point
        """
        return np.sqrt(np.sum(np.power(self.xy - point.xy, 2)))

    def relative_angle(self, point: 'Point') -> np.ndarray:
        """
        Compute angle of connecting line.

        :param point: reference point
        :return: angle in the range (-π, π]
        """
        return np.arctan2(point.y - self.y, point.x - self.x)


class Line:
    """Line object defined by two points a and b."""

    def __init__(self, a: Point, b: Point) -> None:
        """
        Create a Line instance.

        :param a: first point
        :param b: second point
        """
        self.a, self.b = a, b

    @property
    def direction_vector(self) -> Point:
        """
        Vector get with b - a.

        :return: direction vector
        """
        return self.b - self.a

    @property
    def norm_vector(self) -> Point:
        """
        Vector perpendicular to directional vector.

        :return: normal vector
        """
        dv = self.direction_vector
        return Point(dv.x, -dv.y, dv.angle)

    @property
    def equation(self) -> np.ndarray:
        """
        Algebraic equation of the Line in form ax + bx = c.

        :return: (a, b, c)
        """
        nv = self.norm_vector
        c = nv.x * self.a.x + nv.y * self.a.y
        return np.array((nv.x, nv.y, c))

    def is_element_of(self, point: Point, atol: float = 1e-9) -> bool:
        """
        Decide whether a given point lies on the Line.

        :param point: reference point
        :param atol: arithmetic tolerance, default 1e-9
        :return: boolean determining whether the point is on the Line
        """
        cross_product = ((point.y - self.a.y) * (self.b.x - self.a.x) -
                         (self.b.y - self.a.y) * (point.x - self.a.x))
        collinear = cross_product < atol
        return collinear


class Segment(Line):
    """Line, except it is adjusted to fit general geometric properties."""

    def __init__(self, a: Point, b: Point) -> None:
        """
        Create a Segment instance.

        :param a: first point
        :param b: second point
        """
        super().__init__(a, b)

    @property
    def midpoint(self) -> Point:
        """
        Compute a point in between a and b.

        :return: midpoint
        """
        return (self.a + self.b) / 2

    def is_element_of(self, point: Point, atol: float = 1e-9) -> bool:
        """
        Decide whether a given point lies on the Segment.

        :param point: reference point
        :param atol: arithmetic tolerance, default 1e-9
        :return: boolean determining whether the point is on the Segment
        """
        within_bounds = (min(self.a.x, self.b.x) - atol <= point.x <=
                         max(self.a.x, self.b.x) + atol and
                         min(self.a.y, self.b.y) - atol <= point.y <=
                         max(self.a.y, self.b.y) + atol)
        return super().is_element_of(point, atol) and within_bounds


class Circle:
    """Circle object defined by a center point c and radius r."""

    def __init__(self, c: Point, r: float) -> None:
        """
        Create Circle instance.

        :param c: center
        :param r: radius
        """
        self.c, self.r = c, r

    def is_inner(self, point: Point) -> bool:
        """
        Decide whether a given point lies in the inner part of the Circle.

        :param point: reference point
        :return: boolean determining whether the point is in the Circle
        """
        return (np.square(point.x - self.c.x) + np.square(point.y - self.c.y)
                <= np.square(self.r))


def intersection(circle: Circle, linear: Union[Line, Segment]) -> list:
    """
    Calculate intersects.

    Algorithm based on:
    https://mathworld.wolfram.com/Circle-LineIntersection.html

    :param circle: reference Circle
    :param linear: reference Line or Segment
    :return: list of intersects
    """
    dx = linear.direction_vector.x
    dy = linear.direction_vector.y
    dr = np.sqrt(np.square(dx) + np.square(dy))
    d = np.linalg.det(((linear.a.x - circle.c.x, linear.b.x - circle.c.x),
                       (linear.a.y - circle.c.y, linear.b.y - circle.c.y)))
    delta = np.square(circle.r) * np.square(dr) - np.square(d)
    if delta < 0:
        return []
    else:
        sign_dy = -1 if dy < 0 else 1
        x1 = (d * dy + sign_dy * dx * np.sqrt(delta)) / np.square(dr)
        y1 = (-d * dx + abs(dy) * np.sqrt(delta)) / np.square(dr)
        x2 = (d * dy - sign_dy * dx * np.sqrt(delta)) / np.square(dr)
        y2 = (-d * dx - abs(dy) * np.sqrt(delta)) / np.square(dr)
        p1 = Point(x1 + circle.c.x, y1 + circle.c.y)
        p2 = Point(x2 + circle.c.x, y2 + circle.c.y)
        intersects = []
        if linear.is_element_of(p1):
            intersects.append(p1)
        if linear.is_element_of(p2):
            intersects.append(p2)
        return intersects


if __name__ == "__main__":
    print(intersection(Circle(Point(0, 1), 5),
                       Segment(Point(6, 4), Point(-2, 4))))
