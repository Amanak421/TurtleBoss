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

