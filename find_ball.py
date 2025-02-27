import cv2
import numpy as np

import scipy.io

# Read .mat file
data = scipy.io.loadmat("test3.mat")
rgb_img = data["image_rgb"]

# Convert to HSV
hsv = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)#overeno Tomem

########################
# Definování rozsahu pro žlutou barvu
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([30, 255, 255])

# Maskování pouze žlutých oblastí
mask = cv2.inRange(hsv, lower_yellow, upper_yellow)


# Najdeme obrysy (kontury) v masce
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if contours:
    # Najdeme největší obrys (předpokládáme, že míč je největší objekt)
    largest_contour = max(contours, key=cv2.contourArea)

    # Najdeme obalující kruh kolem největšího obrysu
    (x, y), radius = cv2.minEnclosingCircle(largest_contour)
    center = (int(x), int(y))
    radius = int(radius)

    # Oprava: Chybělo správné použití obrázku pro kreslení
    output_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)  # Převod na BGR pro kreslení barevných prvků

    # Kreslení detekovaného míče
    cv2.circle(hsv, center, radius, (0, 255, 0), 3)
    cv2.circle(hsv, center, 5, (0, 0, 255), -1)
    print(f"Střed: {center}, radius: {radius}")


######################################

cv2.imshow("Win HSV", hsv)
cv2.imshow("Win RGB", rgb_img)
cv2.waitKey()
cv2.destroyAllWindows() 