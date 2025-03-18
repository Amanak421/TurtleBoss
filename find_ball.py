import cv2
import numpy as np
import scipy.io
from rigidobject import RigidObject, RigidType, ColorType


class ColorMaskBounding:
    def __init__(self, lb, ub, c):
        (self.lb, self.ub, self.c) = (lb, ub, c)

COLOR_BOUNDS_OBST = (
    ColorMaskBounding((90, 150, 65), (110, 255, 210), ColorType.BLUE),
    ColorMaskBounding((40, 50, 50), (85, 200, 200), ColorType.GREEN),
    ColorMaskBounding((0, 150, 110), (10, 255, 255), ColorType.RED)
)

COLOR_BOUND_BALL = ColorMaskBounding((20, 130, 95), (30, 255, 255), ColorType.YELLOW)


MIN_AREA_OBST = 400
MIN_AREA_BALL = 1500

TOP_Y_BORDER = 1/8
BOTTOM_Y_BORDER = 7/8


def find_ball(rgb_img, all_objects) -> None:
    # Convert to HSV
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, COLOR_BOUND_BALL.lb, COLOR_BOUND_BALL.ub)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_c) > MIN_AREA_BALL:
            (x, y), radius = cv2.minEnclosingCircle(largest_c)
            if  rgb_img.shape[0] * TOP_Y_BORDER < y:
                all_objects.append(RigidObject(int(x), int(y), int(radius), int(radius), RigidType.BALL))


def find_obstacles(rgb_img, all_objects) -> None:
    for bound in COLOR_BOUNDS_OBST:
        # Convert to HSV
        hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, bound.lb, bound.ub)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            for cnt in contours:
                if cv2.contourArea(cnt) > MIN_AREA_OBST:
                    _x, _y, w, h = cv2.boundingRect(cnt)

                    ratio = h / w
                    # print(f"Width: {w}, height: {h}, ratio: {ration}")
                    if ratio < 2.5:
                        continue

                    m = cv2.moments(cnt)
                    cx = m['m10'] / m['m00']
                    cy = m['m01'] / m['m00']
                    r_type = RigidType.POLE if bound.c == ColorType.BLUE else RigidType.OBST
                    if rgb_img.shape[0] * TOP_Y_BORDER < cy < rgb_img.shape[0] * BOTTOM_Y_BORDER:
                        all_objects.append(RigidObject(int(cx), int(cy), int(w), int(h), r_type, bound.c))


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
        # rgb_img_ = cv2.imread("test_data/block_ball.png")
        # print(f"W: {rgb_img_.shape[1]}, H: {rgb_img_.shape[0]}")  # TODO delete
        # cv2.line(rgb_img_,  (0,int(rgb_img_.shape[0] * TOP_Y_BORDER)), (int(rgb_img_.shape[1]), int(rgb_img_.shape[0] * TOP_Y_BORDER)), (30, 60, 90), thickness=5)  # TODO delete
        # cv2.line(rgb_img_,  (0,int(rgb_img_.shape[0] * BOTTOM_Y_BORDER)), (int(rgb_img_.shape[1]), int(rgb_img_.shape[0] * BOTTOM_Y_BORDER)), (130, 160, 190), thickness=5)  # TODO delete
        all_objects_ = find_objects(rgb_img_)
        show_objects(rgb_img_, all_objects_, window_, wait=True)
        print(all_objects_)
    cv2.destroyAllWindows()
