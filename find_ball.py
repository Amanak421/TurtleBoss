import cv2
import numpy as np
import scipy.io


LOWER_YELLOW = np.array([20, 100, 100])
UPPER_YELLOW = np.array([30, 255, 255])

# Blue, Green, Red
LOWER_OBSTACLES = np.array([100, 50, 157], [40, 50, 50], [0, 75, 50])
UPPER_OBSTACLES = np.array([140, 140, 157], [90, 255, 255], [10, 255, 255])

"""
Modrá (H: 100–140)
Min: H = 100, S = 50, V = 50
Max: H = 140, S = 140, V = 157

Zelená (H: 40–90)
Min: H = 40, S = 50, V = 50
Max: H = 90, S = 255, V = 255

Červená (první rozsah, H: 0–10)
Min: H = 0, S = 50, V = 50
Max: H = 10, S = 255, V = 255

Červená (druhý rozsah, H: 170–180)
Min: H = 170, S = 50, V = 50
Max: H = 179, S = 145, V = 153



"""






def find_ball(rgb_img, lower_y = LOWER_YELLOW, upper_y = UPPER_YELLOW) -> tuple | None:
    # Convert to HSV
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_y, upper_y)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)

        (x, y), radius = cv2.minEnclosingCircle(largest_contour)
        center = (int(x), int(y))
        radius = int(radius)

        draw_circle(rgb_img, center, radius)

        return center, radius
    else:
        return None

#TODO
def find_obstacles(rgb_img, lower_y = LOWER_YELLOW, upper_y = UPPER_YELLOW) -> tuple | None:
    # Convert to HSV
    hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_y, upper_y)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)

        (x, y), radius = cv2.minEnclosingCircle(largest_contour)
        center = (int(x), int(y))
        radius = int(radius)

        draw_circle(rgb_img, center, radius)

        return center, radius
    else:
        return None


def draw_circle(rgb_img, center, r) -> None:
    rgb_img = np.array(rgb_img, dtype=np.uint8)
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2BGRA)##FIXME###????
    cv2.circle(rgb_img, center, r, (0, 255, 0), 3)
    cv2.circle(rgb_img, center, 5, (0, 0, 255), -1)
    print(f"Center: {center}, radius: {r}")
    

    #cv2.imshow("Win HSV", hsv)
    cv2.imshow("Win RGB", rgb_img)
    #cv2.imshow("Win MASK", mask)
    cv2.waitKey()
    cv2.destroyAllWindows() 


def load_img(filename):
    data = scipy.io.loadmat(filename)
    rgb_img = data["image_rgb"]
    return rgb_img

for i in range(1,6):
    # Read .mat file
    rgb_img = load_img(f"test_data/test_y{i}.mat")
    find_ball(rgb_img)