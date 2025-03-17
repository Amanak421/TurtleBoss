import cv2
import numpy as np
import scipy.io
from enum import Enum

LOWER_YELLOW = np.array([20, 130, 95])
UPPER_YELLOW = np.array([30, 255, 255])

# Blue, Green, Red
LOWER_OBSTACLES = np.array([[90, 150, 65], [40, 50, 50], [0, 150, 110]])
UPPER_OBSTACLES = np.array([[110, 255, 210], [85, 200, 200], [10, 255, 255]])

RADIUS_POLE = 0.025
RADIUS_BALL = 0.11

MIN_AREA_OBST = 400
MIN_AREA_BALL = 1500

TOP_Y_BORDER = 1/8
BOTTOM_Y_BORDER = 7/8

class RigidType(Enum):
    BALL = 1
    POLE = 2
    OBST = 3

class ColorType(Enum):
    YELLOW = 1
    BLUE = 2
    GREEN = 3
    RED = 4

COLOR_TYPE = np.array([ColorType.BLUE, ColorType.GREEN, ColorType.RED])

class RigidObject:
    def __init__(self, x, y, w, h, o_type: RigidType, c_type:ColorType):
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
        self.x = pc[self.im_y][self.im_x][2] #+ r * vector[0] / norm
        self.y = -pc[self.im_y][self.im_x][0] #+ r * vector[1] / norm

        print("TEST PRINT X Y: ", self.x, self.y)


def find_ball(rgb_img, all_objects, lower_y=LOWER_YELLOW, upper_y=UPPER_YELLOW) -> None:
    # Convert to HSV
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_y, upper_y)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_c) > MIN_AREA_BALL:
            (x, y), radius = cv2.minEnclosingCircle(largest_c)
            if  rgb_img.shape[0] * TOP_Y_BORDER < y:
                all_objects.append(RigidObject(int(x), int(y), int(radius), int(radius), RigidType.BALL, ColorType.YELLOW))


def find_obstacles(rgb_img, all_objects, lower_o=LOWER_OBSTACLES, upper_o=UPPER_OBSTACLES) -> None:
    for i in range(np.size(lower_o, 0)):
        # Convert to HSV
        hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_o[i], upper_o[i])

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            for cnt in contours:
                if cv2.contourArea(cnt) > MIN_AREA_OBST:
                    _x, _y, w, h = cv2.boundingRect(cnt)

                    ration = h / w
                    #print(f"Width: {w}, height: {h}, ratio: {ration}")
                    if ration < 2.5:
                        continue

                    m = cv2.moments(cnt)
                    cx = (m['m10']/m['m00'])
                    cy = (m['m01']/m['m00'])
                    r_type = RigidType.POLE if i == 0 else RigidType.OBST
                    if  rgb_img.shape[0] * TOP_Y_BORDER < cy < rgb_img.shape[0] * BOTTOM_Y_BORDER:
                        all_objects.append(RigidObject(int(cx), int(cy), int(w), int(h), r_type, COLOR_TYPE[i]))


def draw_circle(rgb_img, x, y, r):
    rgb_img = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)
    cv2.circle(rgb_img, (x, y), r, (0, 255, 255), 3)
    cv2.circle(rgb_img, (x, y), 3, (0, 0, 255), -1)
    return rgb_img


def draw_rectangle(rgb_img, obst):
    rgb_img = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)
    x1, y1 = (obst.im_x - obst.w // 2), (obst.im_y - obst.h // 2)
    x2, y2 = (obst.im_x + obst.w // 2), (obst.im_y + obst.h // 2)
    r_color = (255, 0, 0) if obst.o_type == RigidType.POLE else (0, 0, 255)
    cv2.rectangle(rgb_img, (x1, y1), (x2, y2), r_color, 2)
    cv2.circle(rgb_img, (obst.im_x, obst.im_y), 3, (0, 0, 255), -1)
    return rgb_img


def show_objects(rgb_img, all_objects, window, wait=False) -> None:
    for obj in all_objects:
        if obj.o_type == RigidType.BALL:
            rgb_img = draw_circle(rgb_img, obj.im_x, obj.im_y, obj.w)
        else:
            rgb_img = draw_rectangle(rgb_img, obj)
    cv2.imshow(window, rgb_img)
    if wait:
        cv2.waitKey()
    else:
        cv2.waitKey(5)# & 0xFF == ord('q')
    

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

        #rgb_img_ = cv2.imread("test_data/block_ball.png")
        #print(f"W: {rgb_img_.shape[1]}, H: {rgb_img_.shape[0]}")#XXX
        #cv2.line(rgb_img_,  (0,int(rgb_img_.shape[0] * TOP_Y_BORDER)), (int(rgb_img_.shape[1]), int(rgb_img_.shape[0] * TOP_Y_BORDER)), (30, 60, 90), thickness=5)#XXX
        #cv2.line(rgb_img_,  (0,int(rgb_img_.shape[0] * BOTTOM_Y_BORDER)), (int(rgb_img_.shape[1]), int(rgb_img_.shape[0] * BOTTOM_Y_BORDER)), (130, 160, 190), thickness=5)#XXX
        all_objects_ = find_objects(rgb_img_)
        show_objects(rgb_img_, all_objects_, window_, wait=True)
        print(all_objects_)
    cv2.destroyAllWindows()
