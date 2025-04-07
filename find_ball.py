"""Computer vision module based on cv2."""


import cv2
import numpy as np
from rigidobject import ColorType, RigidObject, RigidType
import scipy.io


class ColorMaskBounding:
    """Template for masking data: lower and upper bounds, color itself."""

    def __init__(self, lb: tuple, ub: tuple, c: ColorType) -> None:
        """
        Create ColorMaskBounding instance.

        :param lb: lower boundary
        :param ub: upper boundary
        :param c: color
        """
        (self.lb, self.ub, self.c) = (lb, ub, c)


COLOR_BOUNDS_OBST = (
    ColorMaskBounding((90, 180, 90), (110, 255, 200), ColorType.BLUE),
    ColorMaskBounding((40, 50, 50), (85, 200, 200), ColorType.GREEN),
    ColorMaskBounding((0, 150, 110), (10, 255, 255), ColorType.RED)
)

COLOR_BOUND_BALL = ColorMaskBounding((21, 140, 80), (30, 255, 255),
                                     ColorType.YELLOW)



MIN_AREA_OBST = 200
MIN_AREA_BALL = 800

TOP_Y_BORDER = 1 / 8
BOTTOM_Y_BORDER = 7 / 8


def find_ball(rgb_img: np.ndarray, all_objects: list) -> None:
    """
    Find and add ball to all_objects.

    :param rgb_img: RGB image
    :param all_objects: list of objects
    """
    # Convert to HSV
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, COLOR_BOUND_BALL.lb, COLOR_BOUND_BALL.ub)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    contours = list(c for c in contours if cv2.contourArea(c) > MIN_AREA_BALL)
    contours.sort(key=cv2.contourArea, reverse=True)

    for c in contours:
        (x, y), radius = cv2.minEnclosingCircle(c)
        if rgb_img.shape[0] * TOP_Y_BORDER < y:
            all_objects.append(RigidObject(int(x), int(y),
                                           int(radius), int(radius),
                                           RigidType.BALL))
            break


def find_obstacles(rgb_img: np.ndarray, all_objects: list) -> None:
    """
    Find and add obstacles to all_objects.

    :param rgb_img: RGB image
    :param all_objects: list of objects
    """
    for bound in COLOR_BOUNDS_OBST:
        # Convert to HSV
        hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, bound.lb, bound.ub)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            for cnt in contours:
                if cv2.contourArea(cnt) > MIN_AREA_OBST:
                    _x, _y, w, h = cv2.boundingRect(cnt)

                    ratio = h / w
                    if ratio < 2.5:
                        continue

                    m = cv2.moments(cnt)
                    cx = m['m10'] / m['m00']
                    cy = m['m01'] / m['m00']
                    r_type = RigidType.POLE if bound.c == ColorType.BLUE else (
                        RigidType.OBST)
                    if (rgb_img.shape[0] * TOP_Y_BORDER < cy <
                            rgb_img.shape[0] * BOTTOM_Y_BORDER):
                        all_objects.append(RigidObject(int(cx), int(cy),
                                                       int(w), int(h),
                                                       r_type, bound.c))


def draw_circle(rgb_img: np.ndarray, x: int, y: int, r: int) -> np.ndarray:
    """
    Add circle to rgb_img on (x, y) with radius r.

    Used for visualization and testing purposes.

    :param rgb_img: RGB image
    :param x: x coordinate
    :param y: y coordinate
    :param r: radius
    :return: RGB image
    """
    rgb_img: np.ndarray = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)
    cv2.circle(rgb_img, (x, y), r, (0, 255, 255), 3)
    cv2.circle(rgb_img, (x, y), 3, (0, 0, 255), -1)
    return rgb_img


def draw_rectangle(rgb_img: np.ndarray, obst: RigidObject) -> np.ndarray:
    """
    Add rectangle around obstacle obst to rgb_img.

    Used for visualization and testing purposes.

    :param rgb_img: RGB image
    :param obst: Obstacle
    :return: RGB image
    """
    rgb_img = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)
    x1, y1 = ((obst.im_position[0] - obst.w // 2),
              (obst.im_position[1] - obst.h // 2))
    x2, y2 = ((obst.im_position[0] + obst.w // 2),
              (obst.im_position[1] + obst.h // 2))
    r_color = (255, 0, 0) if obst.o_type == RigidType.POLE else (0, 0, 255)
    cv2.rectangle(rgb_img, (x1, y1), (x2, y2), r_color, 2)
    cv2.circle(rgb_img, (obst.im_position[0], obst.im_position[1]),
               3, (0, 0, 255), -1)
    return rgb_img


def show_objects(rgb_img: np.ndarray,
                 all_objects: list,
                 window: str,
                 wait: bool = False) -> None:
    """
    Show all_objects.

    Used for visualization and testing purposes.

    :param rgb_img: RGB image
    :param all_objects: list of visible objects
    :param window: the name of cv2.namedWindow
    :param wait: boolean switch, set to True for testing
    """
    for obj in all_objects:
        if obj.o_type == RigidType.BALL:
            rgb_img = draw_circle(rgb_img, obj.im_position[0],
                                  obj.im_position[1], obj.w)
        else:
            rgb_img = draw_rectangle(rgb_img, obj)
    cv2.imshow(window, rgb_img)
    if wait:
        cv2.waitKey()
    else:
        cv2.waitKey(5)  # & 0xFF == ord('q')


def load_img(filename: str) -> np.ndarray:
    """
    Load matlab .mat file as though as it was regular RGB image.

    :param filename: filepath to matlab .mat file
    :return: RGB image
    """
    data = scipy.io.loadmat(filename)
    rgb_img = data["image_rgb"]
    return rgb_img


def find_objects(rgb_img: np.ndarray) -> list:
    """
    Initialize list of objects all_objects and fill it with visible objects.

    :param rgb_img: RGB image
    :return: list of objects
    """
    all_objects = []
    find_ball(rgb_img, all_objects)
    find_obstacles(rgb_img, all_objects)
    return all_objects


if __name__ == "__main__":
    window_ = "RGB all objects"
    cv2.namedWindow(window_)
    for img_index in range(49, 55):
        rgb_img_ = cv2.imread(f"test_data/test_p{img_index}.png")
        #rgb_img_ = load_img(f"test_data/test_p{img_index}.mat")
        all_objects_ = find_objects(rgb_img_)
        show_objects(rgb_img_, all_objects_, window_, wait=True)
        print(all_objects_)
    cv2.destroyAllWindows()
