from __future__ import print_function

import sys
from datetime import datetime
from robolab_turtlebot import Turtlebot, sleep, Rate, get_time
from scipy.io import savemat
from math import pi

turtle = Turtlebot(rgb=True, depth=True, pc=True)
sleep(2)
turtle.play_sound(1)
sleep(0.3)

test = Move(None, None)
print(test.getPosition())
test.go(1)
print(test.getPosition())
test.rotate(pi/2)
print(test.getPosition())
test.go(1)
print(test.getPosition())
test.rotate(pi/2)
print(test.getPosition())
test.go(1)
print(test.getPosition())
test.rotate(pi/2)
print(test.getPosition())
test.go(1)
print(test.getPosition())
test.rotate(pi/2)
print(test.getPosition())