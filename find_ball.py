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
        largest_contour = max(contours, key=cv2.contourArea)
        if largest_contour > MIN_AREA:
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)
            all_objects.append(RigidObject(int(x), int(y), int(radius), int(radius), RigidType.BALL))


def find_obstacles(rgb_img, lower_o=LOWER_OBSTACLES, upper_o=UPPER_OBSTACLES) -> None:
    obstacles_dict = {}
    for i in range(np.size(lower_o, 0)):

        # Convert to HSV
        hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_o[i], upper_o[i])

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 500

        if contours:
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    if i not in obstacles_dict:
                        obstacles_dict[i] = [[x, y, w, h]]
                    else:
                        obstacles_dict[i].append([x, y, w, h])

    return obstacles_dict


def draw_circle(rgb_img, center, r) -> None:
    rgb_img = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)
    cv2.circle(rgb_img, center, r, (0, 255, 255), 3)
    cv2.circle(rgb_img, center, 5, (0, 0, 255), -1)
    # print(f"Center: {center}, radius: {r}")
    return rgb_img


def draw_rectangles(rgb_img, obstacles_dict) -> None:
    rgb_img = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)
    color_arr = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for key in obstacles_dict:
        for rec in obstacles_dict[key]:
            [x, y, w, h] = rec
            cv2.rectangle(rgb_img, (x, y), (x + w, y + h), color_arr[key], 2)
    return rgb_img



def show_objects(rgb_img, center, radius, obstacles_dict) -> None:
    rgb_img = draw_circle(rgb_img, center, radius)
    rgb_img = draw_rectangles(rgb_img, obstacles_dict)
    # rgb_img = draw_center(rgb_img, obstacles_center_dict)

    cv2.imshow("RGB all objects", rgb_img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def load_img(filename):
    data = scipy.io.loadmat(filename)
    rgb_img = data["image_rgb"]
    return rgb_img


def find_objects(rgb_img):
    all_objects = []
    find_ball(rgb_img, all_objects)
    obstacles_dict = find_obstacles(rgb_img)
    show_objects(rgb_img, center, radius, obstacles_dict)
    return all_objects


if __name__ == "__main__":
    for img_index in range(1, 9):
        rgb_img_ = load_img(f"test_data/test_y{img_index}.mat")
        find_objects(rgb_img_)
