#!/usr/bin/env python

import cv2

from robolab_turtlebot import Turtlebot, detector

WINDOW = 'markers'


def main():

    turtle = Turtlebot(rgb=True)
    cv2.namedWindow(WINDOW)

    while not turtle.is_shutting_down():
        # get point cloud
        image = turtle.get_rgb_image()

        # wait for image to be ready
        if image is None:
            continue

        # detect markers in the image
        markers = detector.detect_markers(image)

        # draw markers in the image
        detector.draw_markers(image, markers)

        # show image
        cv2.imshow(WINDOW, image)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
