"""Module for calibration and debug of colors."""

# This testing script was inspired by:
# https://pastebin.com/MJfWmD6W


import cv2
import numpy as np
import scipy.io

color_pick = []


def mouse_callback(event: any, x: any, y: any, flags: any, param: any) -> None:
    """Select a pixel using the callback function."""
    if event == cv2.EVENT_LBUTTONDOWN:
        img = param
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_value = hsv[y, x]
        color_pick.append(hsv_value)
        print(f"Picked HSV: {hsv_value}")


def main() -> None:
    """Easy to use GUI app."""
    for img_index in range(1, 2):
        #data = scipy.io.loadmat(f"../test_data/test_p{img_index}.mat")
        #img = data["image_rgb"]
        img = cv2.imread("test_data/test_p1.png")

        if img is None:
            print(f"Cannot read: test_data/test_{img_index}.mat")
            continue

        """for file in os.listdir("new_photos"):
        file_path = os.path.join("new_photos", file)
        data = scipy.io.loadmat(file_path)
        img = data["image_rgb"]"""
        cv2.imshow("Pick pixel or Esc", img)
        cv2.setMouseCallback("Pick pixel or Esc", mouse_callback, param=img)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
        cv2.destroyAllWindows()

    np.array(color_pick)
    print(f"Color_pick array: {color_pick}")

    if len(color_pick) == 0:
        print("No colors picked")
        return

    min_hsv = np.min(color_pick, axis=0)
    max_hsv = np.max(color_pick, axis=0)
    median_hsv = np.median(color_pick, axis=0)

    print("\n--- Results ---")
    print(f"Min HSV: {min_hsv}")
    print(f"Max HSV: {max_hsv}")
    print(f"Average HSV: {median_hsv}")


if __name__ == "__main__":
    main()
