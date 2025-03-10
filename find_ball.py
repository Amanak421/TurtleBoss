import cv2
import numpy as np
import scipy.io
from enum import Enum

LOWER_YELLOW = np.array([20, 100, 100])
UPPER_YELLOW = np.array([30, 255, 255])

# Blue, Green, Red
LOWER_OBSTACLES = np.array([[90, 100, 50], [40, 50, 50], [0, 75, 50]])
UPPER_OBSTACLES = np.array([[130, 255, 255], [90, 255, 255], [10, 255, 255]])

MIN_AREA = 500

class RigidType(Enum):
    BALL = 1
    POLE = 2
    OBST = 3


class RigidObject:
    def __init__(self, x, y, w, h, o_type: RigidType):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.o_type = o_type

    def __repr__(self):
        return f"{self.o_type.name}\t on {self.x}, {self.y}"

    def __str__(self):
        return self.__repr__()


def find_ball(rgb_img, all_objects, lower_y=LOWER_YELLOW, upper_y=UPPER_YELLOW) -> None:
    # Convert to HSV
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_y, upper_y)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_c) > MIN_AREA:
            (x, y), radius = cv2.minEnclosingCircle(largest_c)
            all_objects.append(RigidObject(int(x), int(y), int(radius), int(radius), RigidType.BALL))


def find_obstacles(rgb_img, all_objects, lower_o=LOWER_OBSTACLES, upper_o=UPPER_OBSTACLES) -> None:
    for i in range(np.size(lower_o, 0)):
        # Convert to HSV
        hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_o[i], upper_o[i])

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            for cnt in contours:
                if cv2.contourArea(cnt) > MIN_AREA:
                    _x, _y, w, h = cv2.boundingRect(cnt)
                    M = cv2.moments(cnt)
                    cx = (M['m10']/M['m00'])
                    cy = (M['m01']/M['m00'])
                    r_type = RigidType.POLE if i == 0 else RigidType.OBST
                    all_objects.append(RigidObject(int(cx), int(cy), int(w), int(h), r_type))


def draw_circle(rgb_img, x, y, r):
    rgb_img = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)
    cv2.circle(rgb_img, (x, y), r, (0, 255, 255), 3)
    cv2.circle(rgb_img, (x, y), 3, (0, 0, 255), -1)
    return rgb_img


def draw_rectangle(rgb_img, obst):
    rgb_img = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)
    x1, y1 = int(obst.x - obst.w // 2), int(obst.y - obst.h // 2)
    x2, y2 = int(obst.x + obst.w // 2), int(obst.y + obst.h // 2)
    r_color = (255, 0, 0) if obst.o_type == RigidType.POLE else (0, 0, 255)
    cv2.rectangle(rgb_img, (x1, y1), (x2, y2), r_color, 2)
    cv2.circle(rgb_img, (obst.x, obst.y), 3, (0, 0, 255), -1)
    return rgb_img


def show_objects(rgb_img, all_objects, window, wait=False) -> None:
    for obj in all_objects:
        if obj.o_type == RigidType.BALL:
            rgb_img = draw_circle(rgb_img, obj.x, obj.y, obj.w)
        else:
            rgb_img = draw_rectangle(rgb_img, obj)
    cv2.imshow(window, rgb_img)
    if wait: cv2.waitKey()
    

def load_img(filename):
    data = scipy.io.loadmat(filename)
    rgb_img = data["image_rgb"]
    return rgb_img


def find_objects(rgb_img):
    all_objects = []
    find_ball(rgb_img, all_objects)
    find_obstacles(rgb_img, all_objects)
    return all_objects


if __name__ == "__main__":
    window_ = "RGB all objects"
    cv2.namedWindow(window_)
    for img_index in range(1, 9):
        rgb_img_ = load_img(f"test_data/test_y{img_index}.mat")
        all_objects_ = find_objects(rgb_img_)
        show_objects(rgb_img_, all_objects_, window_, wait=True)
        print(all_objects_)
    cv2.destroyAllWindows()
