import numpy as np


def normalize_angle(angle):
        return np.arctan2(np.sin(angle), np.cos(angle))

class Point:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle

    def __repr__(self) -> str:
        return f"({self.x}, {self.y}, {self.angle})"

    def __str__(self) -> str:
        return self.__repr__()
    
    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y, self.angle)

    def __sub__(self, point):
        return Point(self.x - point.x, self.y - point.y, self.angle)

    @property
    def xya(self):
        return np.array((self.x, self.y, self.angle))
    
    @property
    def xy(self):
        return np.array((self.x, self.y))

    @property
    def sin(self):
        return np.sin(self.angle)

    @property
    def cos(self):
        return np.cos(self.angle)   
    
    @property
    def homog_xy(self):
        return np.array((self.x, self.y, 1))
    
    def add_angle(self, angle) -> None:
        self.angle = normalize_angle(self.angle + angle)

    def distance(self, point):
        return np.sqrt(np.sum(np.power(self.xy - point.xy, 2)))
    
    def relative_angle(self, point):
        """Compute angle of connecting line."""
        return np.arctan2(point.y - self.y, point.x - self.x)


class Segment:
    def __init__(self, a: Point, b: Point):
        self.a, self.b = a, b

    @property
    def direction_vector(self):
        return self.b - self.a

    @property
    def norm_vector(self):
        dv = self.direction_vector
        return Point(dv.x, -dv.y, dv.angle)

    @property
    def equation(self):
        # ax + bx = c
        nv = self.norm_vector
        c = nv.x * self.a.x + nv.y * self.a.y
        return np.array((nv.x, nv.y, c))

    def is_element_of(self, point: Point, atol=1e-9):
        cross_product = (point.y - self.a.y) * (self.b.x - self.a.x) - (self.b.y - self.a.y) * (point.x - self.a.x)
        collinear = cross_product < atol
        within_bounds = (min(self.a.x, self.b.x) - atol <= point.x <= max(self.a.x, self.b.x) + atol and
                         min(self.a.y, self.b.y) - atol <= point.y <= max(self.a.y, self.b.y) + atol)
        return collinear and within_bounds



class Circle:
    def __init__(self, c: Point, r: float):
        self.c, self.r = c, r


def intersection(circle: Circle, segment: Segment):
    # https://mathworld.wolfram.com/Circle-LineIntersection.html
    dx = segment.direction_vector.x
    dy = segment.direction_vector.y
    dr = np.sqrt(np.sum(np.square(dx), np.square(dy)))
    d = np.linalg.det(((segment.a.x - circle.c.x, segment.b.x - circle.c.x), (segment.a.y - circle.c.y, segment.b.y - circle.c.y)))
    delta = np.square(circle.r) * np.square(dr) - np.square(d)
    if delta < 0:
        return []
    else:
        sign_dy = -1 if dy < 0 else 1
        x1 = (d * dy + sign_dy * dx * np.sqrt(delta)) / np.square(dr)
        y1 = (-d * dx + abs(dy) * np.sqrt(delta)) / np.square(dr)
        x2 = (d * dy - sign_dy * dx * np.sqrt(delta)) / np.square(dr)
        y2 = (-d * dx + abs(dy) * np.sqrt(delta)) / np.square(dr)
        p1 = Point(x1 + circle.c.x, y1 + circle.c.y)
        p2 = Point(x2 + circle.c.x, y2 + circle.c.y)
        intersects = []
        if segment.is_element_of(p1): intersects.append(p1)
        if segment.is_element_of(p2): intersects.append(p2)
        return intersects


if __name__ == "__main__":
    print(intersection(Circle(Point(0, 1), 5), Segment(Point(6, 4), Point(-2, 4))))
